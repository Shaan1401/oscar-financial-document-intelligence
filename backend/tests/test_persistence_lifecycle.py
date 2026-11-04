"""
OSCAR — Database Persistence & Lifecycle Integration Test Suite
Validates SQLite WAL persistence, ACID compliance, cascading relationships,
classification/review persistence, reconciliation calculation persistence,
export consistency, rollback semantics, and multi-record preservation.
All tests execute against an isolated temporary SQLite database.
"""

import uuid
from decimal import Decimal
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.database.models import (
    Statement,
    Account,
    Transaction,
    ClassificationEvent,
    ReviewEvent,
    AuditEvent,
)
from app.exports.excel_exporter import ExcelExporter
from app.exports.csv_exporter import CSVExporter
from app.validation.normalizer import FinancialNormalizer


@pytest.fixture
def isolated_db(tmp_path):
    """
    Creates a dedicated, isolated SQLite database in WAL mode with foreign keys enabled.
    Yields (session, session_factory, engine).
    """
    db_file = tmp_path / f"test_isolated_{uuid.uuid4().hex[:8]}.db"
    test_engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(test_engine, "connect")
    def configure_pragmas(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=test_engine)
    SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionFactory()

    try:
        yield session, SessionFactory, test_engine
    finally:
        session.close()
        test_engine.dispose()


def test_01_new_statement_creation_and_persistence(isolated_db):
    """Test 1: Statement creation and persistent reload across new session."""
    session, SessionFactory, _ = isolated_db

    stmt_id = str(uuid.uuid4())
    statement = Statement(
        id=stmt_id,
        filename="bank_statement_q3.pdf",
        file_hash="a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef",
        file_path="storage/bank_statement_q3.pdf",
        bank_name="OSCAR National Test Bank",
        layout_type="generic",
        pdf_type="text",
        page_count=2,
        status="PROCESSED",
        opening_balance_minor=5000000,
        closing_balance_minor=7500000,
        total_debits_minor=2500000,
        total_credits_minor=5000000,
        currency="INR",
        exponent=2,
    )
    session.add(statement)
    session.commit()
    session.close()

    # Reopen in a completely new session
    new_session = SessionFactory()
    try:
        loaded = new_session.query(Statement).filter(Statement.id == stmt_id).first()
        assert loaded is not None, "Statement must be retrievable in new session"
        assert loaded.filename == "bank_statement_q3.pdf"
        assert loaded.bank_name == "OSCAR National Test Bank"
        assert loaded.opening_balance_minor == 5000000
        assert loaded.closing_balance_minor == 7500000
        assert loaded.currency == "INR"
    finally:
        new_session.close()


def test_02_transaction_creation_and_cascade_relationship(isolated_db):
    """Test 2: Transaction linkage to statement and cascade delete verification."""
    session, SessionFactory, _ = isolated_db

    stmt_id = str(uuid.uuid4())
    stmt = Statement(
        id=stmt_id,
        filename="cascade_test.pdf",
        file_hash="1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        file_path="storage/cascade_test.pdf",
        status="PROCESSED",
    )
    session.add(stmt)
    session.flush()

    for i in range(1, 4):
        txn = Transaction(
            statement_id=stmt_id,
            date="2026-10-0" + str(i),
            description=f"TEST TRANSACTION #{i}",
            raw_description=f"RAW TEST TRANSACTION #{i}",
            debit_minor=100000 * i,
            credit_minor=0,
            balance_minor=5000000 - (100000 * i),
            currency="INR",
            exponent=2,
            category="Office Supplies",
            row_sequence=i,
        )
        session.add(txn)
    session.commit()
    session.close()

    # Verify transactions linked to statement
    s2 = SessionFactory()
    try:
        txns = s2.query(Transaction).filter(Transaction.statement_id == stmt_id).all()
        assert len(txns) == 3, "All 3 transactions must exist"

        # Cascade delete test
        stmt_to_delete = s2.query(Statement).filter(Statement.id == stmt_id).first()
        s2.delete(stmt_to_delete)
        s2.commit()

        remaining_txns = s2.query(Transaction).filter(Transaction.statement_id == stmt_id).all()
        assert len(remaining_txns) == 0, "Transactions must be deleted via cascade when statement is deleted"
    finally:
        s2.close()


def test_03_retrieval_after_database_session_close_and_recreation(isolated_db):
    """Test 3: Absolute disk persistence across total session destruction and recreation."""
    session, SessionFactory, engine = isolated_db

    stmt_id = str(uuid.uuid4())
    stmt = Statement(
        id=stmt_id,
        filename="session_lifecycle.pdf",
        file_hash="ffff0000ffff0000ffff0000ffff0000ffff0000ffff0000ffff0000ffff0000",
        file_path="storage/session_lifecycle.pdf",
        status="PROCESSED",
    )
    account = Account(
        statement_id=stmt_id,
        account_number="987654321098",
        holder_name="OSCAR Research Lab",
        masked_number="XXXXXXXX1098",
        ifsc_code="OSCB0009999",
        branch="Bengaluru Main",
    )
    session.add(stmt)
    session.add(account)
    session.commit()

    # Completely destroy the session
    session.close()
    del session

    # Create fresh session directly from engine
    FreshSession = sessionmaker(bind=engine)
    s_fresh = FreshSession()
    try:
        reloaded_stmt = s_fresh.query(Statement).filter(Statement.id == stmt_id).first()
        assert reloaded_stmt is not None
        assert reloaded_stmt.filename == "session_lifecycle.pdf"

        reloaded_acc = s_fresh.query(Account).filter(Account.statement_id == stmt_id).first()
        assert reloaded_acc is not None
        assert reloaded_acc.holder_name == "OSCAR Research Lab"
        assert reloaded_acc.masked_number == "XXXXXXXX1098"
    finally:
        s_fresh.close()


def test_04_classification_persistence_rule_and_ml(isolated_db):
    """Test 4: Classification events persistence for both RULE and ML methods."""
    session, SessionFactory, _ = isolated_db

    stmt_id = str(uuid.uuid4())
    stmt = Statement(id=stmt_id, filename="class_test.pdf", file_hash="hash_class", file_path="p", status="PROCESSED")
    session.add(stmt)
    session.flush()

    # Transaction 1: Rule-based
    t1 = Transaction(statement_id=stmt_id, date="2026-10-01", description="UPI/SWIGGY MEALS", raw_description="UPI/SWIGGY MEALS", debit_minor=45000, credit_minor=0, balance_minor=955000, category="Food & Dining", classification_method="RULE", confidence_score=1.0)
    session.add(t1)
    session.flush()

    c1 = ClassificationEvent(
        transaction_id=t1.id,
        method="RULE",
        category="Food & Dining",
        confidence_score=1.0,
        rule_id="RULE-FOOD-01",
        explanation="Exact keyword match 'SWIGGY' in Food & Dining dictionary",
    )
    session.add(c1)

    # Transaction 2: ML-based
    t2 = Transaction(statement_id=stmt_id, date="2026-10-02", description="MISC CONSULTANCY SVC", raw_description="MISC CONSULTANCY SVC", debit_minor=0, credit_minor=300000, balance_minor=1255000, category="Professional Services", classification_method="ML", confidence_score=0.91)
    session.add(t2)
    session.flush()

    c2 = ClassificationEvent(
        transaction_id=t2.id,
        method="ML",
        category="Professional Services",
        confidence_score=0.91,
        explanation="Dual TF-IDF Logistic Regression model prediction with confidence 0.91",
    )
    session.add(c2)
    session.commit()
    session.close()

    # Verify reload in fresh session
    s_verify = SessionFactory()
    try:
        events = s_verify.query(ClassificationEvent).all()
        assert len(events) == 2
        methods = {e.method: e for e in events}
        assert "RULE" in methods
        assert methods["RULE"].category == "Food & Dining"
        assert methods["RULE"].rule_id == "RULE-FOOD-01"

        assert "ML" in methods
        assert methods["ML"].category == "Professional Services"
        assert methods["ML"].confidence_score == 0.91
        assert "Dual TF-IDF" in methods["ML"].explanation
    finally:
        s_verify.close()


def test_05_manual_category_correction_persistence(isolated_db):
    """Test 5: Manual category correction, review event audit logging, and persistence."""
    session, SessionFactory, _ = isolated_db

    stmt_id = str(uuid.uuid4())
    stmt = Statement(id=stmt_id, filename="correction_test.pdf", file_hash="hash_corr", file_path="p", status="PROCESSED")
    session.add(stmt)
    session.flush()

    txn = Transaction(
        statement_id=stmt_id,
        date="2026-10-03",
        description="CBDT TAX CHALLAN 280",
        raw_description="CBDT TAX CHALLAN 280",
        debit_minor=500000,
        credit_minor=0,
        balance_minor=1000000,
        category="Other / Unclassified",
        classification_method="ML",
        confidence_score=0.62,
        review_status="FLAGGED",
    )
    session.add(txn)
    session.commit()
    txn_id = txn.id

    # User performs manual correction
    txn_to_correct = session.query(Transaction).filter(Transaction.id == txn_id).first()
    prev_cat = txn_to_correct.category
    txn_to_correct.category = "Tax & Government"
    txn_to_correct.classification_method = "MANUAL"
    txn_to_correct.review_status = "CORRECTED"

    review_event = ReviewEvent(
        transaction_id=txn_id,
        action="CORRECTED",
        old_category=prev_cat,
        new_category="Tax & Government",
        reason="Verified as advance tax payment challan ITNS 280",
    )
    session.add(review_event)
    session.commit()
    session.close()

    # Reopen and confirm manual correction survived
    s2 = SessionFactory()
    try:
        reloaded_txn = s2.query(Transaction).filter(Transaction.id == txn_id).first()
        assert reloaded_txn.category == "Tax & Government"
        assert reloaded_txn.classification_method == "MANUAL"
        assert reloaded_txn.review_status == "CORRECTED"

        rev = s2.query(ReviewEvent).filter(ReviewEvent.transaction_id == txn_id).first()
        assert rev is not None
        assert rev.old_category == "Other / Unclassified"
        assert rev.new_category == "Tax & Government"
        assert rev.action == "CORRECTED"
    finally:
        s2.close()


def test_06_reconciliation_persistence_and_recalculation(isolated_db):
    """Test 6: Reconciliation minor-unit math persistence and state updates."""
    session, SessionFactory, _ = isolated_db

    stmt_id = str(uuid.uuid4())
    stmt = Statement(
        id=stmt_id,
        filename="recon_test.pdf",
        file_hash="hash_recon",
        file_path="p",
        opening_balance_minor=10000000,  # ₹100,000.00
        total_credits_minor=5000000,     # ₹50,000.00
        total_debits_minor=3000000,      # ₹30,000.00
        closing_balance_minor=12000000,  # ₹120,000.00
        expected_closing_minor=12000000, # ₹120,000.00
        variance_minor=0,
        reconciliation_status="RECONCILED",
        status="PROCESSED",
    )
    session.add(stmt)
    session.commit()
    session.close()

    # Reload and verify
    s2 = SessionFactory()
    try:
        reloaded = s2.query(Statement).filter(Statement.id == stmt_id).first()
        expected = reloaded.opening_balance_minor + reloaded.total_credits_minor - reloaded.total_debits_minor
        assert expected == reloaded.expected_closing_minor
        assert reloaded.variance_minor == (reloaded.closing_balance_minor - reloaded.expected_closing_minor)
        assert reloaded.variance_minor == 0
        assert reloaded.reconciliation_status == "RECONCILED"
    finally:
        s2.close()


def test_07_audit_event_persistence(isolated_db):
    """Test 7: Audit log persistence, chronological order, and structured metadata."""
    session, SessionFactory, _ = isolated_db

    stmt_id = str(uuid.uuid4())
    stmt = Statement(id=stmt_id, filename="audit_test.pdf", file_hash="h_audit", file_path="p", status="PROCESSED")
    session.add(stmt)
    session.flush()

    events = [
        AuditEvent(actor="SYSTEM", event_type="UPLOAD", statement_id=stmt_id, details="File uploaded"),
        AuditEvent(actor="SYSTEM", event_type="EXTRACTION", statement_id=stmt_id, details="10 transactions extracted"),
        AuditEvent(actor="USER", event_type="CORRECTION", statement_id=stmt_id, details="Txn #1 category updated"),
        AuditEvent(actor="SYSTEM", event_type="RECONCILIATION", statement_id=stmt_id, details="Reconciled successfully"),
        AuditEvent(actor="USER", event_type="EXPORT", statement_id=stmt_id, details="Exported XLSX workbook"),
    ]
    session.add_all(events)
    session.commit()
    session.close()

    s2 = SessionFactory()
    try:
        loaded_events = s2.query(AuditEvent).filter(AuditEvent.statement_id == stmt_id).order_by(AuditEvent.id.asc()).all()
        assert len(loaded_events) == 5
        types = [e.event_type for e in loaded_events]
        assert types == ["UPLOAD", "EXTRACTION", "CORRECTION", "RECONCILIATION", "EXPORT"]
        assert loaded_events[2].actor == "USER"
    finally:
        s2.close()


def test_08_export_data_consistency(isolated_db):
    """Test 8: Export consistency between SQLite database records and generated Excel/CSV."""
    session, SessionFactory, _ = isolated_db

    stmt_id = str(uuid.uuid4())
    stmt = Statement(
        id=stmt_id,
        filename="export_verify.pdf",
        file_hash="h_export",
        file_path="p",
        opening_balance_minor=5000000,
        closing_balance_minor=7500000,
        total_debits_minor=2500000,
        total_credits_minor=5000000,
        expected_closing_minor=7500000,
        variance_minor=0,
        reconciliation_status="RECONCILED",
        status="PROCESSED",
    )
    acc = Account(
        statement_id=stmt_id,
        account_number="50100234891234",
        holder_name="OSCAR Enterprise User",
        ifsc_code="OSCB0001234",
    )
    txns = [
        Transaction(
            statement_id=stmt_id,
            date="2026-10-01",
            description="SALARY CREDIT FROM ACME CORP",
            raw_description="SALARY CREDIT FROM ACME CORP",
            debit_minor=0,
            credit_minor=5000000,
            balance_minor=10000000,
            category="Salary & Income",
            classification_method="RULE",
            confidence_score=1.0,
            row_sequence=1,
        ),
        Transaction(
            statement_id=stmt_id,
            date="2026-10-02",
            description="OFFICE SUPPLIES PURCHASE",
            raw_description="OFFICE SUPPLIES PURCHASE",
            debit_minor=2500000,
            credit_minor=0,
            balance_minor=7500000,
            category="Office Supplies",
            classification_method="MANUAL",
            confidence_score=1.0,
            review_status="CORRECTED",
            row_sequence=2,
        ),
    ]
    session.add(stmt)
    session.add(acc)
    session.add_all(txns)
    session.commit()

    # 1. Generate Excel and verify
    excel_bytes = ExcelExporter.export_statement(stmt, txns, acc)
    assert len(excel_bytes) > 2000, "Excel output must contain valid workbook bytes"

    # 2. Generate CSV and verify
    csv_text = CSVExporter.export_transactions(txns)
    assert "SALARY CREDIT FROM ACME CORP" in csv_text
    assert "OFFICE SUPPLIES PURCHASE" in csv_text
    assert "50000.00" in csv_text  # Minor unit 5000000 -> 50000.00
    assert "25000.00" in csv_text  # Minor unit 2500000 -> 25000.00
    session.close()


def test_09_rollback_on_failed_processing_operation(isolated_db):
    """Test 9: Database rollback semantics on unexpected processing errors."""
    session, SessionFactory, _ = isolated_db

    stmt_id = str(uuid.uuid4())
    stmt = Statement(id=stmt_id, filename="rollback_test.pdf", file_hash="h_rb", file_path="p", status="PROCESSED")
    session.add(stmt)
    session.commit()

    # Simulate an error inside a transactional block
    try:
        t_bad = Transaction(
            statement_id=stmt_id,
            date="2026-10-01",
            description="CORRUPTED TRANSACTION",
            raw_description="CORRUPTED TRANSACTION",
            debit_minor=1000,
            credit_minor=0,
            balance_minor=1000,
            category="Test",
        )
        session.add(t_bad)
        session.flush()

        # Simulate exception during downstream processing
        raise ValueError("Simulated parsing abort or network fault")
    except ValueError:
        session.rollback()

    # Verify database state after rollback
    count = session.query(Transaction).filter(Transaction.statement_id == stmt_id).count()
    assert count == 0, "No transactions should persist after explicit rollback"
    session.close()


def test_10_preservation_of_existing_records(isolated_db):
    """Test 10: Operations on a new statement never mutate or delete existing statements."""
    session, SessionFactory, _ = isolated_db

    # Baseline: Statement A
    id_a = str(uuid.uuid4())
    stmt_a = Statement(id=id_a, filename="statement_a.pdf", file_hash="hash_a", file_path="p_a", status="PROCESSED")
    txn_a = Transaction(statement_id=id_a, date="2026-10-01", description="TXN A", raw_description="TXN A", debit_minor=1000, credit_minor=0, balance_minor=9000, category="Groceries")
    session.add_all([stmt_a, txn_a])
    session.commit()

    # Operation on Statement B
    id_b = str(uuid.uuid4())
    stmt_b = Statement(id=id_b, filename="statement_b.pdf", file_hash="hash_b", file_path="p_b", status="PROCESSED")
    txn_b = Transaction(statement_id=id_b, date="2026-10-02", description="TXN B", raw_description="TXN B", debit_minor=2000, credit_minor=0, balance_minor=8000, category="Utilities")
    session.add_all([stmt_b, txn_b])
    session.commit()

    # Verify Statement A remains untouched
    s2 = SessionFactory()
    try:
        reloaded_a = s2.query(Statement).filter(Statement.id == id_a).first()
        assert reloaded_a is not None
        assert reloaded_a.filename == "statement_a.pdf"

        reloaded_txns_a = s2.query(Transaction).filter(Transaction.statement_id == id_a).all()
        assert len(reloaded_txns_a) == 1
        assert reloaded_txns_a[0].description == "TXN A"
    finally:
        s2.close()
