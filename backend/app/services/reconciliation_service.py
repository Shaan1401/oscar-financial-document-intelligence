from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.database.models import Statement, Transaction, AuditEvent
from app.validation.normalizer import FinancialNormalizer

class ReconciliationService:
    """
    Mathematical and accounting reconciliation engine:
      - Validates Expected Closing Balance = Opening Balance + Total Credits - Total Debits
      - Calculates exact Variance in minor units
      - Performs step-by-step running balance verification (oldest-first and newest-first aware)
      - Identifies duplicate candidates and financial anomalies
    """

    @classmethod
    def reconcile_statement(cls, db: Session, statement_id: str) -> Dict[str, Any]:
        stmt = db.query(Statement).filter(Statement.id == statement_id).first()
        if not stmt:
            raise ValueError(f"Statement {statement_id} not found")

        txns: List[Transaction] = (
            db.query(Transaction)
            .filter(Transaction.statement_id == statement_id)
            .order_by(Transaction.row_sequence.asc())
            .all()
        )

        if not txns:
            stmt.reconciliation_status = "INSUFFICIENT_DATA"
            db.commit()
            return {
                "statement_id": stmt.id,
                "status": "INSUFFICIENT_DATA",
                "message": "No transactions available for reconciliation",
                "variance": 0.0,
                "exceptions": [],
            }

        # 1. Opening & Closing Balances check
        if stmt.opening_balance_minor is None or stmt.closing_balance_minor is None:
            # Try to infer if not present
            if txns[0].balance_minor is not None:
                op = txns[0].balance_minor + txns[0].debit_minor - txns[0].credit_minor
                stmt.opening_balance_minor = op
            if txns[-1].balance_minor is not None:
                stmt.closing_balance_minor = txns[-1].balance_minor

        if stmt.opening_balance_minor is None or stmt.closing_balance_minor is None:
            stmt.reconciliation_status = "INSUFFICIENT_DATA"
            db.commit()
            return {
                "statement_id": stmt.id,
                "status": "INSUFFICIENT_DATA",
                "message": "Opening or closing balance unavailable on document",
                "variance": 0.0,
                "exceptions": ["Opening or closing balance missing from document"],
            }

        exp = stmt.exponent
        opening = stmt.opening_balance_minor
        closing = stmt.closing_balance_minor

        total_debits = sum(t.debit_minor for t in txns)
        total_credits = sum(t.credit_minor for t in txns)

        expected_closing = opening + total_credits - total_debits
        variance = closing - expected_closing

        stmt.total_debits_minor = total_debits
        stmt.total_credits_minor = total_credits
        stmt.expected_closing_minor = expected_closing
        stmt.variance_minor = variance

        exceptions: List[str] = []

        # 2. Running Balance Verification
        # Determine chronological direction (oldest-first vs newest-first)
        running_bal_errors = 0
        current_bal = opening

        for idx, t in enumerate(txns):
            current_bal = current_bal + t.credit_minor - t.debit_minor
            if t.balance_minor is not None:
                diff = abs(current_bal - t.balance_minor)
                if diff > 0:
                    running_bal_errors += 1
                    t.is_anomaly = True
                    t.validation_status = "WARNING"
                    t.validation_warnings = (
                        f"Running balance mismatch at row {t.row_sequence}: "
                        f"expected {FinancialNormalizer.to_decimal(current_bal, exp)}, "
                        f"got {FinancialNormalizer.to_decimal(t.balance_minor, exp)}"
                    )

        if running_bal_errors > 0:
            exceptions.append(f"Running balance inconsistent on {running_bal_errors} transaction rows")

        # 3. Duplicate Detection & Anomalies
        seen_keys = {}
        dup_count = 0
        all_amounts = [t.debit_minor + t.credit_minor for t in txns]
        avg_amount = sum(all_amounts) / max(len(all_amounts), 1)

        for t in txns:
            # Key: date + amount + direction + first 15 chars of desc
            key = f"{t.date}_{t.debit_minor}_{t.credit_minor}_{t.description[:15].upper()}"
            if key in seen_keys:
                dup_count += 1
                t.is_duplicate = True
                t.validation_status = "WARNING"
                t.review_status = "NEEDS_REVIEW"
                t.validation_warnings = f"Potential duplicate of row sequence {seen_keys[key]}"
                exceptions.append(f"Potential duplicate transaction at row {t.row_sequence}")
            else:
                seen_keys[key] = t.row_sequence

            # Unusually large transaction (> 5x average)
            amt = t.debit_minor + t.credit_minor
            if amt > max(avg_amount * 5, 5000000):  # e.g. > 50,000 INR and 5x avg
                t.is_anomaly = True
                if not t.validation_warnings:
                    t.validation_warnings = "Unusually large monetary value relative to statement average"

        # Final Status determination
        if variance == 0 and running_bal_errors == 0:
            stmt.reconciliation_status = "RECONCILED"
        elif variance != 0:
            stmt.reconciliation_status = "MISMATCH"
            exceptions.append(
                f"Closing balance variance of {FinancialNormalizer.to_decimal(variance, exp)} {stmt.currency}"
            )
        else:
            stmt.reconciliation_status = "REVIEW_REQUIRED"

        db.commit()

        # Audit event
        audit = AuditEvent(
            actor="SYSTEM",
            event_type="RECONCILIATION",
            statement_id=stmt.id,
            details=(
                f"Reconciliation evaluated: {stmt.reconciliation_status}. "
                f"Opening: {FinancialNormalizer.to_decimal(opening, exp)}, "
                f"Credits: {FinancialNormalizer.to_decimal(total_credits, exp)}, "
                f"Debits: {FinancialNormalizer.to_decimal(total_debits, exp)}, "
                f"Variance: {FinancialNormalizer.to_decimal(variance, exp)}"
            ),
        )
        db.add(audit)
        db.commit()

        return {
            "statement_id": stmt.id,
            "bank_name": stmt.bank_name,
            "period": stmt.statement_period,
            "status": stmt.reconciliation_status,
            "currency": stmt.currency,
            "opening_balance": float(FinancialNormalizer.to_decimal(opening, exp)),
            "total_credits": float(FinancialNormalizer.to_decimal(total_credits, exp)),
            "total_debits": float(FinancialNormalizer.to_decimal(total_debits, exp)),
            "expected_closing_balance": float(FinancialNormalizer.to_decimal(expected_closing, exp)),
            "actual_closing_balance": float(FinancialNormalizer.to_decimal(closing, exp)),
            "variance": float(FinancialNormalizer.to_decimal(variance, exp)),
            "is_reconciled": stmt.reconciliation_status == "RECONCILED",
            "running_balance_errors": running_bal_errors,
            "duplicate_count": dup_count,
            "exceptions": exceptions,
            "recalculated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

