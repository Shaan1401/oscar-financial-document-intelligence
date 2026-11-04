import pytest
from pathlib import Path
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.database.session import Base, get_db, init_db, engine
from app.database.models import Statement, Account, Transaction
from app.extraction.pdf_validator import PDFValidator
from app.extraction.text_extractor import DocumentExtractor
from app.bank_parsers.generic import GenericBankParser
from app.services.statement_processor import StatementProcessor
from app.core.errors import InvalidPDFError

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    yield

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def sample_pdf_path():
    path = settings.SAMPLE_DATA_DIR / "pdf" / "synthetic_statement_layout_a.pdf"
    assert path.exists(), f"Sample PDF missing at {path}"
    return path

def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "OSCAR"
    assert "ocr_available" in data

def test_pdf_validator_rejects_invalid_bytes():
    fake_content = b"NOT_A_PDF_DOCUMENT_123456"
    with pytest.raises(InvalidPDFError):
        PDFValidator.validate_file_content(fake_content, "fake.pdf")

def test_pdf_validator_accepts_valid_pdf(sample_pdf_path):
    with open(sample_pdf_path, "rb") as f:
        content = f.read()
    sha256_hash, safe_name, page_count = PDFValidator.validate_file_content(content, "sample.pdf")
    assert len(sha256_hash) == 64
    assert safe_name.endswith(".pdf")
    assert page_count >= 1

def test_text_and_table_extraction(sample_pdf_path):
    extracted = DocumentExtractor.extract_document(sample_pdf_path)
    assert extracted["page_count"] >= 1
    assert extracted["pdf_type"] == "text"
    assert len(extracted["pages"]) >= 1

    # Check account metadata extraction
    acc = extracted["account_info"]
    assert acc["bank_name"] is not None
    assert "OSCAR" in acc["bank_name"] or "Bank" in acc["bank_name"]
    assert acc["ifsc_code"] == "OSCB0001234"
    assert acc["account_number"] == "50100234891234"
    assert acc["masked_number"] == "XXXXXXXXXX1234"

def test_generic_bank_parser(sample_pdf_path):
    extracted = DocumentExtractor.extract_document(sample_pdf_path)
    parser = GenericBankParser()
    assert parser.can_parse(extracted) > 0.5

    txns = parser.parse(extracted)
    assert len(txns) == 15, f"Expected 15 transactions, got {len(txns)}"

    first = txns[0]
    assert first.date == "2026-10-01"
    assert "SALARY" in first.description.upper()
    assert first.credit == Decimal("85000.00")
    assert first.debit == Decimal("0.00")
    assert first.balance == Decimal("130000.00")

def test_statement_processing_vertical_slice(client, sample_pdf_path):
    import time
    with open(sample_pdf_path, "rb") as f:
        salted_bytes = f.read() + f"\n% test_vertical_slice_{time.time()}".encode("utf-8")
        files = {"file": ("test_statement_slice.pdf", salted_bytes, "application/pdf")}
    
    response = client.post("/api/v1/statements/upload", files=files)
    assert response.status_code == 200
    stmt_data = response.json()
    assert stmt_data["id"] is not None
    assert stmt_data["status"] == "PROCESSED"
    assert stmt_data["transaction_count"] == 15
    assert stmt_data["total_credits"] == 86899.00
    assert stmt_data["total_debits"] == 49267.50

    statement_id = stmt_data["id"]

    try:
        # 1. Fetch transactions list
        txn_res = client.get(f"/api/v1/transactions?statement_id={statement_id}")
        assert txn_res.status_code == 200
        txns = txn_res.json()["items"]
        assert len(txns) == 15

        # 2. Test Excel Export
        excel_res = client.get(f"/api/v1/exports/{statement_id}/excel")
        assert excel_res.status_code == 200
        assert excel_res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert len(excel_res.content) > 1000

        # 3. Test CSV Export
        csv_res = client.get(f"/api/v1/exports/{statement_id}/csv")
        assert csv_res.status_code == 200
        assert "text/csv" in csv_res.headers["content-type"]
        csv_text = csv_res.content.decode("utf-8")
        assert "Date,Description,Debit,Credit,Balance" in csv_text
        assert "SALARY CREDIT" in csv_text

        # 4. Test Evidence Viewer Page Preview
        preview_res = client.get(f"/api/v1/statements/{statement_id}/pages/1/preview")
        assert preview_res.status_code == 200
        assert preview_res.headers["content-type"] == "image/png"
        assert len(preview_res.content) > 5000
    finally:
        from app.database.session import SessionLocal
        db = SessionLocal()
        try:
            stmt = db.query(Statement).filter(Statement.id == statement_id).first()
            if stmt:
                db.delete(stmt)
                db.commit()
        finally:
            db.close()
