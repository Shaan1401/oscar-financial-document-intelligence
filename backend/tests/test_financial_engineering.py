import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.database.session import SessionLocal
from app.database.models import Statement, Transaction, AuditEvent
from app.services.statement_processor import StatementProcessor
from app.services.reconciliation_service import ReconciliationService
from app.services.review_service import ReviewService

client = TestClient(app)

@pytest.fixture
def processed_statement_id():
    pdf_path = settings.SAMPLE_DATA_DIR / "pdf" / "synthetic_statement_layout_a.pdf"
    with open(pdf_path, "rb") as f:
        content = f.read()

    db = SessionLocal()
    try:
        suffix = uuid.uuid4().hex[:8]
        unique_content = content + f"\n%fin-test-{suffix}".encode("utf-8")
        stmt = StatementProcessor.save_and_validate_upload(db, unique_content, f"fin_test_{suffix}.pdf")
        processed = StatementProcessor.process_statement(db, stmt.id)
        stmt_id = processed.id
    finally:
        db.close()
    return stmt_id

def test_reconciliation_exact_match(processed_statement_id):
    db = SessionLocal()
    try:
        res = ReconciliationService.reconcile_statement(db, processed_statement_id)
        assert res["status"] == "RECONCILED"
        assert res["variance"] == 0.0
        assert res["is_reconciled"] is True
        assert res["opening_balance"] == 45000.00
        assert res["running_balance_errors"] == 0
    finally:
        db.close()

def test_reconciliation_detects_mismatch(processed_statement_id):
    db = SessionLocal()
    try:
        stmt = db.query(Statement).filter(Statement.id == processed_statement_id).first()
        # Artificially alter closing balance by 500.00 INR (50000 minor units)
        original_closing = stmt.closing_balance_minor
        stmt.closing_balance_minor = original_closing + 50000
        db.commit()

        res = ReconciliationService.reconcile_statement(db, processed_statement_id)
        assert res["status"] == "MISMATCH"
        assert res["variance"] == 500.00
        assert res["is_reconciled"] is False
        assert any("Closing balance variance" in ex for ex in res["exceptions"])
    finally:
        db.close()

def test_reconciliation_api_endpoints(processed_statement_id):
    res = client.get(f"/api/v1/reconciliation/{processed_statement_id}")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "opening_balance" in data
    assert "expected_closing_balance" in data

    # Run explicit reconciliation
    res_run = client.post(f"/api/v1/reconciliation/{processed_statement_id}/run")
    assert res_run.status_code == 200
    assert res_run.json()["statement_id"] == processed_statement_id

def test_review_and_approval_workflow(processed_statement_id):
    db = SessionLocal()
    try:
        # Pick one transaction and flag it for review
        txn = db.query(Transaction).filter(Transaction.statement_id == processed_statement_id).first()
        txn.review_status = "NEEDS_REVIEW"
        txn.is_anomaly = True
        txn.validation_warnings = "Flagged for testing human review"
        db.commit()
        txn_id = txn.id
    finally:
        db.close()

    # Verify transaction appears in review queue
    res_queue = client.get(f"/api/v1/reviews?statement_id={processed_statement_id}")
    assert res_queue.status_code == 200
    q_data = res_queue.json()
    assert q_data["total"] >= 1
    flagged_ids = [item["id"] for item in q_data["items"]]
    assert txn_id in flagged_ids

    # Approve transaction
    res_approve = client.post(f"/api/v1/reviews/{txn_id}/approve", json={"reason": "Verified genuine expense"})
    assert res_approve.status_code == 200
    assert res_approve.json()["review_status"] == "APPROVED"

def test_review_correction_workflow(processed_statement_id):
    db = SessionLocal()
    try:
        txn = db.query(Transaction).filter(Transaction.statement_id == processed_statement_id).first()
        txn_id = txn.id
        old_cat = txn.category
    finally:
        db.close()

    # Correct transaction category to "Investments"
    res_correct = client.post(f"/api/v1/reviews/{txn_id}/correct", json={
        "new_category": "Investments",
        "reason": "Reclassified to Investments after receipt check"
    })
    assert res_correct.status_code == 200
    assert res_correct.json()["category"] == "Investments"
    assert res_correct.json()["review_status"] == "CORRECTED"

    # Verify audit event was recorded
    res_audit = client.get(f"/api/v1/audit?statement_id={processed_statement_id}&event_type=CORRECTION")
    assert res_audit.status_code == 200
    audit_data = res_audit.json()
    assert audit_data["total"] >= 1
    assert any("Investments" in item["details"] for item in audit_data["items"])

def test_analytics_endpoints():
    res_summary = client.get("/api/v1/analytics/summary")
    assert res_summary.status_code == 200
    s_data = res_summary.json()
    assert s_data["total_statements"] >= 1
    assert s_data["total_transactions"] >= 1
    assert "total_debits" in s_data
    assert "total_credits" in s_data

    res_cat = client.get("/api/v1/analytics/categories")
    assert res_cat.status_code == 200
    assert isinstance(res_cat.json(), list)
    assert len(res_cat.json()) >= 1

    res_flow = client.get("/api/v1/analytics/cashflow")
    assert res_flow.status_code == 200
    assert isinstance(res_flow.json(), list)

    res_dist = client.get("/api/v1/analytics/distribution")
    assert res_dist.status_code == 200
    assert isinstance(res_dist.json(), list)

