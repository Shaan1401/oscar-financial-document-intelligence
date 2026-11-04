from typing import Dict, Any, Optional
from app.core.config import settings
from app.validation.normalizer import FinancialNormalizer
from app.classification.rule_engine import RuleEngine
from app.classification.ml_engine import MLEngine

class HybridClassifier:
    """
    Two-tiered hybrid classification orchestrator:
      Tier 1: Heuristic rule engine with conflict detection.
      Tier 2: Traditional ML (TF-IDF + Logistic Regression) with confidence gating.
      Fallback: Flagged for human review (NEEDS_REVIEW).
    Strictly Non-LLM.
    """

    def __init__(self, rule_engine: Optional[RuleEngine] = None):
        self.rule_engine = rule_engine or RuleEngine()

    def classify(self, description: str) -> Dict[str, Any]:
        """
        Classifies a transaction description.
        Returns:
          {
            "category": str,
            "classification_method": "RULE_BASED" | "MACHINE_LEARNING" | "NEEDS_REVIEW",
            "confidence_score": float,
            "classification_reason": str,
            "rule_id": Optional[str],
            "model_version": Optional[str],
            "review_status": "APPROVED" | "NEEDS_REVIEW",
          }
        """
        clean_desc = FinancialNormalizer.clean_text(description)
        if not clean_desc:
            return {
                "category": "Other / Unclassified",
                "classification_method": "NEEDS_REVIEW",
                "confidence_score": 0.0,
                "classification_reason": "Empty or invalid transaction description",
                "rule_id": None,
                "model_version": None,
                "review_status": "NEEDS_REVIEW",
            }

        # 1. Tier 1: Rule Engine
        rule_res = self.rule_engine.classify(clean_desc)
        if rule_res:
            if rule_res["has_conflict"]:
                return {
                    "category": "Other / Unclassified",
                    "classification_method": "NEEDS_REVIEW",
                    "confidence_score": 0.50,
                    "classification_reason": rule_res["explanation"],
                    "rule_id": rule_res["rule_id"],
                    "model_version": None,
                    "review_status": "NEEDS_REVIEW",
                }
            else:
                return {
                    "category": rule_res["category"],
                    "classification_method": "RULE_BASED",
                    "confidence_score": 0.99,
                    "classification_reason": rule_res["explanation"],
                    "rule_id": rule_res["rule_id"],
                    "model_version": None,
                    "review_status": "APPROVED",
                }

        # 2. Tier 2: Traditional ML
        ml_cat, ml_score = MLEngine.predict(clean_desc)
        th = settings.ML_CONFIDENCE_THRESHOLD

        if ml_score >= th:
            return {
                "category": ml_cat,
                "classification_method": "MACHINE_LEARNING",
                "confidence_score": ml_score,
                "classification_reason": f"TF-IDF Logistic Regression score {ml_score:.2f} >= {th:.2f}",
                "rule_id": None,
                "model_version": "1.0.0",
                "review_status": "APPROVED",
            }
        else:
            return {
                "category": ml_cat,
                "classification_method": "MACHINE_LEARNING",
                "confidence_score": ml_score,
                "classification_reason": f"Low model confidence ({ml_score:.2f} < {th:.2f}); flagged for review",
                "rule_id": None,
                "model_version": "1.0.0",
                "review_status": "NEEDS_REVIEW",
            }

