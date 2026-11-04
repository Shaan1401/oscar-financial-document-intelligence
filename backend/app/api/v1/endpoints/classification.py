from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.core.config import settings
from app.database.session import get_db
from app.database.models import Transaction, ClassificationEvent
from app.classification.rule_engine import RuleEngine
from app.classification.ml_engine import MLEngine
from app.classification.hybrid_classifier import HybridClassifier
from app.classification.dataset_generator import generate_synthetic_dataset

router = APIRouter(prefix="/classification", tags=["Classification"])

@router.get("/metrics")
def get_classification_metrics():
    """Returns trained model performance metrics, confusion matrix, and threshold curve."""
    metadata = MLEngine.get_metadata()
    metrics = MLEngine.get_metrics()
    if not metadata or not metrics:
        return {
            "status": "NOT_TRAINED",
            "message": "Model has not been trained yet. Call POST /api/v1/classification/retrain to train.",
            "metadata": None,
            "metrics": None,
        }
    return {
        "status": "READY",
        "metadata": metadata,
        "metrics": metrics,
    }

@router.get("/rules")
def get_classification_rules():
    """Returns the complete list of heuristic rules configured in the rule engine."""
    engine = RuleEngine()
    rules = engine.get_all_rules()
    return {
        "count": len(rules),
        "rules": rules,
    }

@router.post("/reclassify")
def reclassify_transaction(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    """
    Classifies a raw description on-the-fly or reclassifies an existing transaction.
    """
    description = payload.get("description")
    txn_id = payload.get("transaction_id")

    if txn_id is not None:
        txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
        if not txn:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if not description:
            description = txn.description

    if not description:
        raise HTTPException(status_code=400, detail="Description is required")

    classifier = HybridClassifier()
    result = classifier.classify(description)

    if txn_id is not None:
        txn.category = result["category"]
        txn.classification_method = result["classification_method"]
        txn.confidence_score = result["confidence_score"]
        txn.classification_reason = result["classification_reason"]
        txn.rule_id = result["rule_id"]
        txn.model_version = result["model_version"]
        txn.review_status = result["review_status"]
        db.commit()

        # Log event
        event = ClassificationEvent(
            transaction_id=txn.id,
            method=result["classification_method"],
            category=result["category"],
            rule_id=result["rule_id"],
            model_version=result["model_version"],
            confidence_score=result["confidence_score"],
            explanation=f"Manual reclassification: {result['classification_reason']}",
        )
        db.add(event)
        db.commit()

    return result

@router.post("/retrain")
def retrain_model():
    """Generates synthetic training dataset and retrains the TF-IDF Logistic Regression pipeline."""
    csv_path = settings.SAMPLE_DATA_DIR / "training" / "synthetic_transactions.csv"
    if not csv_path.exists():
        generate_synthetic_dataset(csv_path, samples_per_category=100)

    results = MLEngine.train_and_evaluate(csv_path)
    return {
        "status": "SUCCESS",
        "message": "Model trained and evaluated successfully",
        "metadata": results["metadata"],
        "test_metrics": results["metrics"]["test_metrics"],
    }

