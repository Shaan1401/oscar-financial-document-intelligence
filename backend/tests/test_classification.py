import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.classification.rule_engine import RuleEngine, Rule
from app.classification.ml_engine import MLEngine
from app.classification.hybrid_classifier import HybridClassifier
from app.database.session import SessionLocal
from app.database.models import Statement
from app.services.statement_processor import StatementProcessor

client = TestClient(app)

def test_rule_engine_matching():
    engine = RuleEngine()

    res_food = engine.classify("UPI/ZOMATO RESTAURANT ORDER")
    assert res_food is not None
    assert res_food["category"] == "Food & Dining"
    assert res_food["rule_id"] == "RULE-FOOD-01"

    res_salary = engine.classify("SALARY CREDIT - TATA CONSULTANCY SERVICES")
    assert res_salary is not None
    assert res_salary["category"] == "Salary & Income"
    assert res_salary["rule_id"] == "RULE-SALARY-01"

    res_atm = engine.classify("ATM CASH WDL HDFC BANK CONNAUGHT")
    assert res_atm is not None
    assert res_atm["category"] == "ATM / Cash Withdrawal"

    res_groc = engine.classify("DMART SUPERMARKET RETAIL PURCHASE")
    assert res_groc is not None
    assert res_groc["category"] == "Groceries"

    res_refund = engine.classify("REFUND AMAZON PAY CANCELLED ORDER")
    assert res_refund is not None
    assert res_refund["category"] == "Refunds & Reversals"

def test_rule_conflict_detection():
    # Construct an engine with conflicting rules at same priority
    conflicting_rules = [
        Rule("RULE-A", "Food & Dining", 100, "contains", "DELIVERY", "Delivery rule"),
        Rule("RULE-B", "Shopping", 100, "contains", "DELIVERY", "Shopping delivery rule"),
    ]
    engine = RuleEngine(conflicting_rules)
    res = engine.classify("EXPRESS DELIVERY ORDER")
    assert res is not None
    assert res["has_conflict"] is True
    assert res["category"] == "Other / Unclassified"
    assert "Conflicting rule matches" in res["explanation"]

def test_ml_engine_prediction():
    cat, score = MLEngine.predict("MONTHLY DISBURSEMENT TECH LABS PAYROLL")
    assert isinstance(cat, str)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0

def test_hybrid_classifier_workflow():
    classifier = HybridClassifier()

    # Rule match
    rule_match = classifier.classify("UPI/SWIGGY BANGALORE IN")
    assert rule_match["classification_method"] == "RULE_BASED"
    assert rule_match["category"] == "Food & Dining"
    assert rule_match["confidence_score"] == 0.99
    assert rule_match["review_status"] == "APPROVED"

    # ML prediction for description without explicit keywords (e.g. trained merchant not in rule engine)
    ml_match = classifier.classify("ACCENTURE SOLUTIONS DISPATCH REF #8934")
    assert ml_match["classification_method"] == "MACHINE_LEARNING"
    assert ml_match["category"] == "Salary & Income"

def test_classification_api_endpoints():
    # Rules list
    res = client.get("/api/v1/classification/rules")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 18
    assert len(data["rules"]) >= 18

    # Metrics
    res_metrics = client.get("/api/v1/classification/metrics")
    assert res_metrics.status_code == 200
    m_data = res_metrics.json()
    assert m_data["status"] == "READY"
    assert "test_metrics" in m_data["metrics"]
    assert m_data["metrics"]["test_metrics"]["accuracy"] >= 0.90

    # On-the-fly reclassify
    res_rec = client.post("/api/v1/classification/reclassify", json={
        "description": "DOMINOS PIZZA OUTLET DINE IN"
    })
    assert res_rec.status_code == 200
    r_json = res_rec.json()
    assert r_json["category"] == "Food & Dining"
    assert r_json["classification_method"] == "RULE_BASED"

def test_statement_processing_assigns_categories():
    pdf_path = settings.SAMPLE_DATA_DIR / "pdf" / "synthetic_statement_layout_a.pdf"
    with open(pdf_path, "rb") as f:
        content = f.read()

    db = SessionLocal()
    stmt_id = None
    try:
        import uuid
        unique_suffix = uuid.uuid4().hex[:8]
        # Append unique PDF comment to create unique SHA-256 hash for test isolation
        unique_content = content + f"\n%test-salt-{unique_suffix}".encode("utf-8")
        test_filename = f"classify_test_{unique_suffix}.pdf"
        stmt = StatementProcessor.save_and_validate_upload(db, unique_content, test_filename)
        stmt_id = stmt.id
        processed = StatementProcessor.process_statement(db, stmt_id)

        assert processed.status == "PROCESSED"
        txns = processed.transactions
        assert len(txns) == 15

        # Verify all transactions have a valid assigned category and method
        for t in txns:
            assert t.category is not None
            assert t.category != ""
            assert t.classification_method in ("RULE_BASED", "MACHINE_LEARNING", "NEEDS_REVIEW")
            assert t.confidence_score is not None

        # Specifically check salary row
        salary_txns = [t for t in txns if "SALARY" in t.description]
        assert len(salary_txns) > 0
        assert salary_txns[0].category == "Salary & Income"

    finally:
        if stmt_id:
            try:
                s_clean = db.query(Statement).filter(Statement.id == stmt_id).first()
                if s_clean:
                    db.delete(s_clean)
                    db.commit()
            except Exception:
                pass
        db.close()
