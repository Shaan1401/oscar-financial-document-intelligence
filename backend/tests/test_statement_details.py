import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.session import SessionLocal
from app.database.models import Statement, Account, Transaction

client = TestClient(app)

def test_statement_detail_valid_id():
    """Verifies that GET /api/v1/statements/{id} returns 200 with statement, account, and transactions."""
    db = SessionLocal()
    # Find any existing statement
    stmt = db.query(Statement).first()
    assert stmt is not None, "At least one statement must exist in test database"
    stmt_id = stmt.id
    db.close()

    res = client.get(f"/api/v1/statements/{stmt_id}")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()

    # 1. Backwards compatible top-level fields
    assert data["id"] == stmt_id
    assert "filename" in data
    assert "transaction_count" in data

    # 2. Contract fields expected by StatementDetails.tsx
    assert "statement" in data, "Must contain nested 'statement' object"
    assert data["statement"]["id"] == stmt_id
    assert "transactions" in data, "Must contain 'transactions' array"
    assert isinstance(data["transactions"], list), "'transactions' must be a list"
    assert len(data["transactions"]) == data["transaction_count"], "Transactions list length must match transaction_count"
    assert "account" in data, "Must contain 'account' field"

def test_statement_detail_unknown_id():
    """Verifies that GET /api/v1/statements/{unknown_id} returns 404 with structured detail."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.get(f"/api/v1/statements/{fake_id}")
    assert res.status_code == 404
    data = res.json()
    assert "detail" in data
    assert fake_id in data["detail"]

def test_statement_detail_empty_transactions():
    """Verifies that a statement with zero transactions returns an empty array [] without errors."""
    db = SessionLocal()
    empty_stmt = Statement(
        filename="empty_statement_for_testing.pdf",
        file_hash="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        file_path="dummy_path.pdf",
        page_count=1,
        status="PROCESSED",
    )
    db.add(empty_stmt)
    db.commit()
    db.refresh(empty_stmt)
    empty_id = empty_stmt.id
    db.close()

    try:
        res = client.get(f"/api/v1/statements/{empty_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == empty_id
        assert data["transactions"] == []
        assert data["transaction_count"] == 0
        assert data["statement"]["id"] == empty_id
    finally:
        # Clean up temporary test statement
        db2 = SessionLocal()
        db2.query(Statement).filter(Statement.id == empty_id).delete()
        db2.commit()
        db2.close()
