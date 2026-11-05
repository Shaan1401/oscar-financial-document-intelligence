import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.session import SessionLocal
from app.database.models import Statement, Transaction, ReviewEvent, AuditEvent
from app.services.analytics_service import AnalyticsService

client = TestClient(app)

@pytest.fixture
def test_statement_with_exceptions():
    """Creates a temporary test statement with pending transactions for review tests."""
    db = SessionLocal()
    try:
        stmt = Statement(
            filename="review_test_statement.pdf",
            file_hash="hash_review_test_12345",
            file_path="dummy_path.pdf",
            bank_name="Test Bank",
            currency="INR",
            exponent=2,
            opening_balance_minor=1000000,
            closing_balance_minor=1500000,
            reconciliation_status="RECONCILED",
            status="PROCESSED",
        )
        db.add(stmt)
        db.flush()

        # Transaction 1: Needs review with anomaly
        t1 = Transaction(
            statement_id=stmt.id,
            date="2026-03-01",
            description="VENDOR PAYMENT HIGH VALUE",
            raw_description="VENDOR PAYMENT HIGH VALUE RAW",
            debit_minor=500000,
            credit_minor=0,
            balance_minor=500000,
            currency="INR",
            exponent=2,
            category="Shopping",
            classification_method="MACHINE_LEARNING",
            confidence_score=0.55,
            classification_reason="Low ML confidence score",
            review_status="NEEDS_REVIEW",
            validation_status="WARNING",
            validation_warnings="Unusually large monetary value relative to statement average",
            is_anomaly=True,
            is_duplicate=False,
            row_sequence=1,
            source_page=1,
        )

        # Transaction 2: Needs review for correction test
        t2 = Transaction(
            statement_id=stmt.id,
            date="2026-03-02",
            description="MISC CHARGE XYZ",
            raw_description="MISC CHARGE XYZ RAW",
            debit_minor=12000,
            credit_minor=0,
            balance_minor=488000,
            currency="INR",
            exponent=2,
            category="Other / Unclassified",
            classification_method="NONE",
            confidence_score=0.40,
            classification_reason="Unclassified expense",
            review_status="NEEDS_REVIEW",
            validation_status="VALID",
            is_anomaly=False,
            is_duplicate=False,
            row_sequence=2,
            source_page=1,
        )

        db.add_all([t1, t2])
        db.commit()
        db.refresh(stmt)
        db.refresh(t1)
        db.refresh(t2)

        yield {
            "statement_id": stmt.id,
            "t1_id": t1.id,
            "t2_id": t2.id,
        }
    finally:
        # Cleanup
        db.query(AuditEvent).filter(AuditEvent.statement_id == stmt.id).delete()
        db.query(ReviewEvent).filter(ReviewEvent.transaction_id.in_([t1.id, t2.id])).delete()
        db.query(Transaction).filter(Transaction.statement_id == stmt.id).delete()
        db.query(Statement).filter(Statement.id == stmt.id).delete()
        db.commit()
        db.close()

def test_approve_transaction_success_and_queue_removal(test_statement_with_exceptions):
    """Test 1-5: Approving a pending transaction persists APPROVED, clears anomalies, and removes it from queue."""
    stmt_id = test_statement_with_exceptions["statement_id"]
    txn_id = test_statement_with_exceptions["t1_id"]

    # 1. Verify it appears in pending review queue
    res_queue = client.get(f"/api/v1/reviews?statement_id={stmt_id}")
    assert res_queue.status_code == 200
    queue_items = res_queue.json()["items"]
    assert any(item["id"] == txn_id for item in queue_items)

    # 2. Click / Call Approve
    res_approve = client.post(
        f"/api/v1/reviews/{txn_id}/approve",
        json={"reason": "Verified legitimate vendor invoice #INV-2026"}
    )
    assert res_approve.status_code == 200
    approve_data = res_approve.json()
    assert approve_data["status"] == "APPROVED"
    assert approve_data["transaction_id"] == txn_id
    assert approve_data["review_status"] == "APPROVED"
    assert "successfully approved" in approve_data["message"]

    # 3. Verify it is immediately removed from the pending review queue
    res_queue_after = client.get(f"/api/v1/reviews?statement_id={stmt_id}")
    assert res_queue_after.status_code == 200
    queue_items_after = res_queue_after.json()["items"]
    assert not any(item["id"] == txn_id for item in queue_items_after)

    # 4. Verify database state directly
    db = SessionLocal()
    try:
        # 4. Verify database state directly:
        # review_status is APPROVED and validation_status is VALID.
        # Original algorithmic detection flags (is_anomaly) are preserved for historical auditability.
        reloaded = db.query(Transaction).filter(Transaction.id == txn_id).first()
        assert reloaded is not None
        assert reloaded.review_status == "APPROVED"
        assert reloaded.validation_status == "VALID"
        assert reloaded.is_anomaly is True  # Preserved for historical accuracy
        assert reloaded.is_duplicate is False

        # 5. Verify ReviewEvent and AuditEvent were created with rich forensic details
        rev_event = db.query(ReviewEvent).filter(ReviewEvent.transaction_id == txn_id).first()
        assert rev_event is not None
        assert rev_event.action == "APPROVE"
        assert "Verified legitimate vendor invoice" in rev_event.reason

        audit_event = db.query(AuditEvent).filter(
            AuditEvent.statement_id == stmt_id,
            AuditEvent.transaction_id == txn_id,
            AuditEvent.event_type == "APPROVAL"
        ).order_by(AuditEvent.id.desc()).first()
        assert audit_event is not None
        assert audit_event.actor == "USER"
        assert "approved by user" in audit_event.details
        assert "anomaly outlier flag" in audit_event.details
    finally:
        db.close()

def test_approve_already_approved_transaction_rejected(test_statement_with_exceptions):
    """Test idempotency: An already approved transaction cannot be approved a second time."""
    txn_id = test_statement_with_exceptions["t1_id"]

    # First approval
    res1 = client.post(f"/api/v1/reviews/{txn_id}/approve", json={"reason": "First approval"})
    assert res1.status_code == 200

    # Duplicate approval attempt
    res2 = client.post(f"/api/v1/reviews/{txn_id}/approve", json={"reason": "Duplicate click"})
    assert res2.status_code == 400
    assert "already approved" in res2.json()["detail"].lower()

def test_approve_nonexistent_transaction_returns_404():
    """Test error handling: Approving non-existent transaction returns 404."""
    res = client.post("/api/v1/reviews/99999999/approve", json={"reason": "Testing 404"})
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_correct_transaction_removes_from_queue_and_audits(test_statement_with_exceptions):
    """Test Correct button functionality: Correcting updates fields and removes from queue."""
    stmt_id = test_statement_with_exceptions["statement_id"]
    txn_id = test_statement_with_exceptions["t2_id"]

    # 1. Correct transaction category and description
    res_correct = client.post(
        f"/api/v1/reviews/{txn_id}/correct",
        json={
            "new_category": "Banking Charges",
            "new_description": "ANNUAL CARD FEE XYZ",
            "reason": "Reclassified after checking statement notes"
        }
    )
    assert res_correct.status_code == 200
    corr_data = res_correct.json()
    assert corr_data["status"] == "CORRECTED"
    assert corr_data["category"] == "Banking Charges"
    assert corr_data["review_status"] == "CORRECTED"

    # 2. Verify removed from review queue
    res_queue = client.get(f"/api/v1/reviews?statement_id={stmt_id}")
    assert res_queue.status_code == 200
    assert not any(item["id"] == txn_id for item in res_queue.json()["items"])

    # 3. Verify audit trail
    res_audit = client.get(f"/api/v1/audit?statement_id={stmt_id}&event_type=CORRECTION")
    assert res_audit.status_code == 200
    audit_items = res_audit.json()["items"]
    assert any(a["transaction_id"] == txn_id for a in audit_items)
