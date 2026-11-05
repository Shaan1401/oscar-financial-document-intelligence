from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.database.models import Transaction, ReviewEvent, AuditEvent, Statement
from app.validation.normalizer import FinancialNormalizer
from app.core.errors import NotFoundError, TransactionStateError

class ReviewService:
    """Manages human review workflows, corrections, audits, and exception approvals."""

    @classmethod
    def get_review_queue(
        cls, db: Session, statement_id: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> Dict[str, Any]:
        query = db.query(Transaction).filter(
            Transaction.review_status.notin_(["APPROVED", "CORRECTED"]),
            (
                (Transaction.review_status == "NEEDS_REVIEW") |
                (Transaction.is_duplicate == True) |
                (Transaction.is_anomaly == True) |
                (Transaction.validation_status.in_(["WARNING", "ANOMALY"]))
            )
        )

        if statement_id:
            query = query.filter(Transaction.statement_id == statement_id)

        total = query.count()
        items = query.order_by(Transaction.id.desc()).offset(offset).limit(limit).all()

        results = []
        for t in items:
            results.append({
                "id": t.id,
                "statement_id": t.statement_id,
                "date": t.date,
                "description": t.description,
                "raw_description": t.raw_description,
                "debit": float(FinancialNormalizer.to_decimal(t.debit_minor, t.exponent)),
                "credit": float(FinancialNormalizer.to_decimal(t.credit_minor, t.exponent)),
                "balance": float(FinancialNormalizer.to_decimal(t.balance_minor, t.exponent)) if t.balance_minor is not None else None,
                "category": t.category,
                "classification_method": t.classification_method,
                "confidence_score": t.confidence_score,
                "classification_reason": t.classification_reason,
                "review_status": t.review_status,
                "validation_status": t.validation_status,
                "validation_warnings": t.validation_warnings,
                "is_duplicate": t.is_duplicate,
                "is_anomaly": t.is_anomaly,
                "source_page": t.source_page,
            })

        return {
            "total": total,
            "items": results,
        }

    @classmethod
    def approve_transaction(cls, db: Session, transaction_id: int, reason: Optional[str] = None) -> Transaction:
        txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not txn:
            raise NotFoundError(f"Transaction #{transaction_id} not found")

        # Guard against duplicate approval if transaction is already approved
        if txn.review_status == "APPROVED":
            raise TransactionStateError(
                f"Transaction #{transaction_id} is already approved and is no longer pending review."
            )

        old_status = txn.review_status
        old_warnings = txn.validation_warnings

        # Update review lifecycle and validation status to APPROVED / VALID
        # Preserve original algorithmic detection flags (is_anomaly, is_duplicate) for forensic history
        txn.review_status = "APPROVED"
        txn.validation_status = "VALID"

        rev_event = ReviewEvent(
            transaction_id=txn.id,
            old_category=txn.category,
            new_category=txn.category,
            action="APPROVE",
            reason=reason or "Human reviewer approved exception",
        )
        db.add(rev_event)

        # Build detailed audit message capturing original detection flags and human review decision
        detection_notes = []
        if txn.is_anomaly:
            detection_notes.append("anomaly outlier flag")
        if txn.is_duplicate:
            detection_notes.append("duplicate flag")
        if old_warnings:
            detection_notes.append(f"warning '{old_warnings}'")

        detection_summary = f" [Original detection: {', '.join(detection_notes)}]" if detection_notes else ""

        audit_details = (
            f"Transaction #{txn.id} approved by user. Previous status: '{old_status}'. "
            f"Reason: {reason or 'Human reviewer approved exception'}.{detection_summary}"
        )

        audit = AuditEvent(
            actor="USER",
            event_type="APPROVAL",
            statement_id=txn.statement_id,
            transaction_id=txn.id,
            details=audit_details,
        )
        db.add(audit)
        db.commit()
        db.refresh(txn)
        return txn

    @classmethod
    def correct_transaction(
        cls,
        db: Session,
        transaction_id: int,
        new_category: Optional[str] = None,
        new_description: Optional[str] = None,
        new_debit: Optional[float] = None,
        new_credit: Optional[float] = None,
        reason: Optional[str] = None,
    ) -> Transaction:
        txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not txn:
            raise NotFoundError(f"Transaction #{transaction_id} not found")

        old_category = txn.category
        old_desc = txn.description
        old_debit = txn.debit_minor
        old_credit = txn.credit_minor
        old_status = txn.review_status

        if new_category:
            txn.category = new_category
            txn.classification_method = "MANUAL"
            txn.classification_reason = f"Manual user correction: {reason or 'User reclassification'}"
            txn.confidence_score = 1.0

        if new_description:
            txn.description = FinancialNormalizer.clean_text(new_description)

        if new_debit is not None:
            txn.debit_minor = FinancialNormalizer.to_minor_units(new_debit, txn.exponent)
        if new_credit is not None:
            txn.credit_minor = FinancialNormalizer.to_minor_units(new_credit, txn.exponent)

        # Update review and validation statuses while preserving historical detection flags
        txn.review_status = "CORRECTED"
        txn.validation_status = "VALID"

        # Log Review Event
        rev_event = ReviewEvent(
            transaction_id=txn.id,
            old_category=old_category,
            new_category=txn.category,
            action="CORRECT",
            reason=reason or f"Corrected by user (Category: {old_category} -> {txn.category})",
        )
        db.add(rev_event)

        # Log Audit Event
        audit = AuditEvent(
            actor="USER",
            event_type="CORRECTION",
            statement_id=txn.statement_id,
            transaction_id=txn.id,
            details=(
                f"Transaction #{txn.id} corrected by user. "
                f"Previous status: '{old_status}'. "
                f"Category: '{old_category}' -> '{txn.category}'. "
                f"Reason: {reason or 'Manual user correction'}."
            ),
        )
        db.add(audit)
        db.commit()
        db.refresh(txn)
        return txn
        return txn

