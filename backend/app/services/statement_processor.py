import os
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import DuplicateDocumentError, ExtractionError
from app.database.models import Statement, Account, Transaction, AuditEvent, ProcessingJob, ClassificationEvent
from app.extraction.pdf_validator import PDFValidator
from app.extraction.text_extractor import DocumentExtractor
from app.bank_parsers.registry import ParserRegistry
from app.validation.normalizer import FinancialNormalizer
from app.classification.hybrid_classifier import HybridClassifier

class StatementProcessor:
    """Orchestrates PDF ingestion, parsing, normalization, and persistence."""

    @classmethod
    def save_and_validate_upload(cls, db: Session, file_content: bytes, original_filename: str) -> Statement:
        # 1. Validate PDF signature and size
        file_hash, safe_name, page_count = PDFValidator.validate_file_content(file_content, original_filename)

        # 2. Check for duplicate upload
        existing = db.query(Statement).filter(Statement.file_hash == file_hash).first()
        if existing:
            raise DuplicateDocumentError(
                f"Document with identical hash already exists (ID: {existing.id})",
                existing_id=existing.id,
            )

        # 3. Save to private local storage
        target_path = settings.STORAGE_DIR / safe_name
        with open(target_path, "wb") as f:
            f.write(file_content)

        # 4. Create Statement record
        statement = Statement(
            filename=original_filename,
            file_hash=file_hash,
            file_path=str(target_path),
            page_count=page_count,
            status="UPLOADED",
        )
        db.add(statement)
        db.commit()
        db.refresh(statement)

        # Record Audit Event
        cls._log_audit(db, "UPLOAD", statement.id, f"Uploaded '{original_filename}' ({len(file_content)} bytes)")
        return statement

    @classmethod
    def process_statement(cls, db: Session, statement_id: str) -> Statement:
        statement = db.query(Statement).filter(Statement.id == statement_id).first()
        if not statement:
            raise ExtractionError(f"Statement {statement_id} not found")

        statement.status = "PROCESSING"
        db.commit()

        try:
            # 1. Document Extraction (PyMuPDF + pdfplumber)
            doc_data = DocumentExtractor.extract_document(statement.file_path)
            statement.pdf_type = doc_data["pdf_type"]
            acc_info = doc_data["account_info"]

            if acc_info.get("bank_name"):
                statement.bank_name = acc_info["bank_name"]
            if acc_info.get("statement_period"):
                statement.statement_period = acc_info["statement_period"]

            # Save Account record
            account = db.query(Account).filter(Account.statement_id == statement.id).first()
            if not account:
                account = Account(
                    statement_id=statement.id,
                    holder_name=acc_info.get("holder_name"),
                    account_number=acc_info.get("account_number"),
                    masked_number=acc_info.get("masked_number"),
                    ifsc_code=acc_info.get("ifsc_code"),
                    branch=acc_info.get("branch"),
                    currency=statement.currency,
                )
                db.add(account)

            # 2. Bank Layout Selection & Parsing
            parser = ParserRegistry.select_parser(doc_data)
            statement.layout_type = parser.layout_type
            parsed_txns = parser.parse(doc_data)

            # Idempotently clear prior transactions if re-processing
            db.query(Transaction).filter(Transaction.statement_id == statement.id).delete()

            # 3. Normalize, Classify & Persist Transactions
            total_debits = Decimal("0.00")
            total_credits = Decimal("0.00")
            first_date = None
            last_date = None

            classifier = HybridClassifier()

            for pt in parsed_txns:
                debit_minor = FinancialNormalizer.to_minor_units(pt.debit, statement.exponent)
                credit_minor = FinancialNormalizer.to_minor_units(pt.credit, statement.exponent)
                balance_minor = FinancialNormalizer.to_minor_units(pt.balance, statement.exponent) if pt.balance is not None else None

                total_debits += pt.debit
                total_credits += pt.credit

                if not first_date:
                    first_date = pt.date
                last_date = pt.date

                # Classify transaction using Hybrid Classifier
                cls_res = classifier.classify(pt.description)

                txn = Transaction(
                    statement_id=statement.id,
                    date=pt.date,
                    description=pt.description,
                    raw_description=pt.raw_description,
                    debit_minor=debit_minor,
                    credit_minor=credit_minor,
                    balance_minor=balance_minor,
                    currency=statement.currency,
                    exponent=statement.exponent,
                    category=cls_res["category"],
                    classification_method=cls_res["classification_method"],
                    confidence_score=cls_res["confidence_score"],
                    classification_reason=cls_res["classification_reason"],
                    rule_id=cls_res["rule_id"],
                    model_version=cls_res["model_version"],
                    review_status=cls_res["review_status"],
                    source_page=pt.source_page,
                    row_sequence=pt.row_sequence,
                    extraction_method=pt.extraction_method,
                    bounding_box=pt.bounding_box,
                    validation_warnings=pt.validation_warnings,
                )
                db.add(txn)
                db.flush()

                # Audit individual classification event
                cls_event = ClassificationEvent(
                    transaction_id=txn.id,
                    method=cls_res["classification_method"],
                    category=cls_res["category"],
                    rule_id=cls_res["rule_id"],
                    model_version=cls_res["model_version"],
                    confidence_score=cls_res["confidence_score"],
                    explanation=cls_res["classification_reason"],
                )
                db.add(cls_event)

            # 4. Summary & Initial Balances
            statement.total_debits_minor = FinancialNormalizer.to_minor_units(total_debits, statement.exponent)
            statement.total_credits_minor = FinancialNormalizer.to_minor_units(total_credits, statement.exponent)
            statement.start_date = first_date
            statement.end_date = last_date

            # Infer opening and closing balances from first and last transactions if present
            if parsed_txns:
                if parsed_txns[-1].balance is not None:
                    statement.closing_balance_minor = FinancialNormalizer.to_minor_units(parsed_txns[-1].balance, statement.exponent)
                if parsed_txns[0].balance is not None:
                    # Opening balance inferred: balance_0 + debit_0 - credit_0
                    op_val = parsed_txns[0].balance + parsed_txns[0].debit - parsed_txns[0].credit
                    statement.opening_balance_minor = FinancialNormalizer.to_minor_units(op_val, statement.exponent)

            statement.status = "PROCESSED"
            db.commit()
            db.refresh(statement)

            # Automatically evaluate reconciliation
            from app.services.reconciliation_service import ReconciliationService
            try:
                ReconciliationService.reconcile_statement(db, statement.id)
            except Exception:
                pass

            cls._log_audit(
                db, "EXTRACTION", statement.id,
                f"Extracted {len(parsed_txns)} transactions using {parser.name}"
            )
            return statement

        except Exception as e:
            statement.status = "FAILED"
            statement.error_message = str(e)
            db.commit()
            cls._log_audit(db, "ERROR", statement.id, f"Extraction failed: {str(e)}")
            raise

    @staticmethod
    def _log_audit(db: Session, event_type: str, statement_id: Optional[str], details: str):
        event = AuditEvent(
            actor="SYSTEM",
            event_type=event_type,
            statement_id=statement_id,
            details=details,
        )
        db.add(event)
        db.commit()
