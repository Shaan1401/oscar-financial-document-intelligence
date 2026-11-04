import sys
from pathlib import Path

# Add backend to python path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.database.session import SessionLocal, init_db
from app.database.models import Statement, Transaction, Account, AuditEvent
from app.services.statement_processor import StatementProcessor
from app.services.reconciliation_service import ReconciliationService
from app.extraction.synthetic_generator import SyntheticStatementGenerator

def seed_demo_data():
    """Generates all synthetic bank statements, ingests them into the database, and reconciles them."""
    print("--- Initializing OSCAR Demonstration Dataset ---")
    init_db()
    db = SessionLocal()

    pdf_dir = ROOT / "sample_data" / "pdf"
    gt_dir = ROOT / "sample_data" / "ground_truth"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    gt_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate statements if missing
    pdf_a = pdf_dir / "synthetic_statement_layout_a.pdf"
    gt_a = gt_dir / "synthetic_statement_layout_a_truth.json"
    if not pdf_a.exists():
        print("Generating Layout A...")
        SyntheticStatementGenerator.generate_layout_a(pdf_a, gt_a)

    pdf_b = pdf_dir / "synthetic_statement_layout_b.pdf"
    gt_b = gt_dir / "synthetic_statement_layout_b_truth.json"
    if not pdf_b.exists():
        print("Generating Layout B...")
        SyntheticStatementGenerator.generate_layout_b(pdf_b, gt_b)

    pdf_c = pdf_dir / "synthetic_statement_layout_c.pdf"
    gt_c = gt_dir / "synthetic_statement_layout_c_truth.json"
    if not pdf_c.exists():
        print("Generating Layout C...")
        SyntheticStatementGenerator.generate_layout_c(pdf_c, gt_c)

    pdf_scanned = pdf_dir / "synthetic_statement_scanned.pdf"
    if not pdf_scanned.exists():
        print("Generating Scanned Statement...")
        SyntheticStatementGenerator.generate_scanned_pdf(pdf_scanned, pdf_a)

    # 2. Ingest digital statements into database
    demo_files = [
        ("synthetic_statement_layout_a.pdf", pdf_a),
        ("synthetic_statement_layout_b.pdf", pdf_b),
        ("synthetic_statement_layout_c.pdf", pdf_c),
    ]

    for filename, path in demo_files:
        with open(path, "rb") as f:
            pdf_bytes = f.read()

        # Check if already in DB
        import hashlib
        f_hash = hashlib.sha256(pdf_bytes).hexdigest()
        existing = db.query(Statement).filter(Statement.file_hash == f_hash).first()

        if existing:
            print(f"Statement '{filename}' already ingested (ID: {existing.id}). Refreshing extraction & reconciling...")
            stmt = StatementProcessor.process_statement(db, existing.id)
            rec = ReconciliationService.reconcile_statement(db, existing.id)
            print(f"  Reconciliation: {rec['status']}, Variance: INR {rec['variance']:.2f}")
        else:
            print(f"Ingesting '{filename}'...")
            stmt = StatementProcessor.save_and_validate_upload(db, pdf_bytes, filename)
            stmt = StatementProcessor.process_statement(db, stmt.id)
            txns_count = len(stmt.transactions)
            print(f"  Successfully extracted {txns_count} transactions.")
            rec = ReconciliationService.reconcile_statement(db, stmt.id)
            print(f"  Reconciliation: {rec['status']}, Variance: INR {rec['variance']:.2f}")

    total_stmts = db.query(Statement).count()
    total_txns = db.query(Transaction).count()
    print(f"\n--- Seeding Complete: {total_stmts} Statements, {total_txns} Transactions in Database ---")
    db.close()

if __name__ == "__main__":
    seed_demo_data()
