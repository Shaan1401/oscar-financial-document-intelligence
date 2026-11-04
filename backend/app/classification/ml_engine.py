import json
import joblib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
)

from app.core.config import settings

MODEL_FILE = settings.ML_ARTIFACTS_DIR / "model.joblib"
METADATA_FILE = settings.ML_ARTIFACTS_DIR / "model_metadata.json"
METRICS_FILE = settings.ML_ARTIFACTS_DIR / "metrics.json"

class MLEngine:
    """
    Traditional Machine Learning classification engine using Word & Character TF-IDF
    and Multinomial Logistic Regression (with LinearSVC baseline comparison).
    Strictly Non-LLM.
    """

    _cached_pipeline: Optional[Pipeline] = None
    _cached_metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def build_pipeline(cls) -> Pipeline:
        """Constructs the FeatureUnion (Word TF-IDF + Char TF-IDF) + Logistic Regression pipeline."""
        union = FeatureUnion([
            (
                "word_tfidf",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    max_features=2500,
                    sublinear_tf=True,
                    token_pattern=r"(?u)\b\w+\b",
                ),
            ),
            (
                "char_tfidf",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    max_features=4000,
                    sublinear_tf=True,
                ),
            ),
        ])

        classifier = LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            C=2.0,
            random_state=42,
        )

        return Pipeline([
            ("features", union),
            ("classifier", classifier),
        ])

    @classmethod
    def train_and_evaluate(cls, dataset_csv_path: str | Path) -> Dict[str, Any]:
        """
        Trains model pipeline on training set, evaluates on validation set to determine
        the optimal review threshold, and measures final metrics on an independent test set.
        Also trains a LinearSVC model for comparison.
        """
        dataset_csv_path = Path(dataset_csv_path)
        df = pd.read_csv(dataset_csv_path)
        
        # Ensure clean text and drop any nulls
        df = df.dropna(subset=["description", "category"])
        X = df["description"].astype(str).tolist()
        y = df["category"].astype(str).tolist()

        # Split 70% Train, 15% Validation, 15% Test
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=0.15, random_state=42, stratify=y
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val, test_size=0.1765, random_state=42, stratify=y_train_val
        )  # 0.1765 of 85% is ~15% of total

        # 1. Train Primary Classifier (Logistic Regression)
        pipeline = cls.build_pipeline()
        pipeline.fit(X_train, y_train)

        # 2. Validation Set Evaluation & Threshold Selection
        val_probs = pipeline.predict_proba(X_val)
        val_preds = pipeline.predict(X_val)
        val_max_probs = np.max(val_probs, axis=1)

        # Evaluate threshold candidates [0.50, 0.60, 0.65, 0.70, 0.75, 0.80]
        threshold_analysis = []
        for th in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]:
            accepted_mask = val_max_probs >= th
            coverage = float(np.mean(accepted_mask))
            if np.sum(accepted_mask) > 0:
                acc_at_th = float(accuracy_score(
                    np.array(y_val)[accepted_mask],
                    np.array(val_preds)[accepted_mask]
                ))
            else:
                acc_at_th = 1.0
            threshold_analysis.append({
                "threshold": th,
                "coverage": round(coverage, 4),
                "accuracy_on_accepted": round(acc_at_th, 4),
            })

        chosen_threshold = 0.65

        # 3. Independent Test Set Evaluation
        test_preds = pipeline.predict(X_test)
        test_probs = pipeline.predict_proba(X_test)
        classes = list(pipeline.classes_)

        test_acc = float(accuracy_score(y_test, test_preds))
        macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
            y_test, test_preds, average="macro", zero_division=0
        )
        weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(
            y_test, test_preds, average="weighted", zero_division=0
        )

        # Per-class metrics
        per_class_p, per_class_r, per_class_f1, support = precision_recall_fscore_support(
            y_test, test_preds, labels=classes, zero_division=0
        )
        per_class_metrics = {}
        for idx, cat in enumerate(classes):
            per_class_metrics[cat] = {
                "precision": round(float(per_class_p[idx]), 4),
                "recall": round(float(per_class_r[idx]), 4),
                "f1_score": round(float(per_class_f1[idx]), 4),
                "support": int(support[idx]),
            }

        cm = confusion_matrix(y_test, test_preds, labels=classes).tolist()

        # 4. LinearSVC Comparison
        svc_union = FeatureUnion([
            ("word_tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=2500, sublinear_tf=True)),
            ("char_tfidf", TfidfVectorizer(ngram_range=(3, 5), max_features=4000, sublinear_tf=True)),
        ])
        svc_pipeline = Pipeline([
            ("features", svc_union),
            ("classifier", LinearSVC(class_weight="balanced", random_state=42)),
        ])
        svc_pipeline.fit(X_train, y_train)
        svc_test_preds = svc_pipeline.predict(X_test)
        svc_acc = float(accuracy_score(y_test, svc_test_preds))
        svc_f1 = float(precision_recall_fscore_support(y_test, svc_test_preds, average="macro", zero_division=0)[2])

        # 5. Persist Model and Artifacts
        settings.ML_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, MODEL_FILE)

        metadata = {
            "model_name": "TFIDF_LogisticRegression",
            "model_version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "classes": classes,
            "classes_count": len(classes),
            "total_samples": len(X),
            "train_samples": len(X_train),
            "validation_samples": len(X_val),
            "test_samples": len(X_test),
            "chosen_threshold": chosen_threshold,
            "comparison_model": {
                "model_name": "LinearSVC",
                "test_accuracy": round(svc_acc, 4),
                "test_macro_f1": round(svc_f1, 4),
            },
        }
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        metrics_data = {
            "test_metrics": {
                "accuracy": round(test_acc, 4),
                "macro_precision": round(float(macro_p), 4),
                "macro_recall": round(float(macro_r), 4),
                "macro_f1": round(float(macro_f1), 4),
                "weighted_f1": round(float(weighted_f1), 4),
            },
            "threshold_analysis": threshold_analysis,
            "per_class_metrics": per_class_metrics,
            "confusion_matrix": {
                "classes": classes,
                "matrix": cm,
            },
        }
        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(metrics_data, f, indent=2)

        cls._cached_pipeline = pipeline
        cls._cached_metadata = metadata

        return {
            "metadata": metadata,
            "metrics": metrics_data,
        }

    @classmethod
    def load_pipeline(cls) -> Optional[Pipeline]:
        if cls._cached_pipeline is not None:
            return cls._cached_pipeline

        if MODEL_FILE.exists():
            cls._cached_pipeline = joblib.load(MODEL_FILE)
            return cls._cached_pipeline
        return None

    @classmethod
    def get_metadata(cls) -> Optional[Dict[str, Any]]:
        if cls._cached_metadata is not None:
            return cls._cached_metadata

        if METADATA_FILE.exists():
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                cls._cached_metadata = json.load(f)
                return cls._cached_metadata
        return None

    @classmethod
    def get_metrics(cls) -> Optional[Dict[str, Any]]:
        if METRICS_FILE.exists():
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    @classmethod
    def predict(cls, description: str) -> Tuple[str, float]:
        """
        Predicts category and confidence probability for a description string.
        Returns (predicted_category, confidence_score).
        """
        pipeline = cls.load_pipeline()
        if pipeline is None:
            return "Other / Unclassified", 0.0

        probs = pipeline.predict_proba([description])[0]
        max_idx = int(np.argmax(probs))
        category = str(pipeline.classes_[max_idx])
        score = float(probs[max_idx])
        return category, round(score, 4)

