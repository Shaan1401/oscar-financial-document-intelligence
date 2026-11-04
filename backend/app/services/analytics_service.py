from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import Statement, Transaction
from app.validation.normalizer import FinancialNormalizer

class AnalyticsService:
    """Database-backed financial analytics and dashboard metrics calculation."""

    @classmethod
    def get_summary(cls, db: Session) -> Dict[str, Any]:
        stmt_count = db.query(Statement).count()
        txn_count = db.query(Transaction).count()

        totals = db.query(
            func.coalesce(func.sum(Transaction.debit_minor), 0),
            func.coalesce(func.sum(Transaction.credit_minor), 0),
        ).first()

        total_debits_minor = totals[0] if totals else 0
        total_credits_minor = totals[1] if totals else 0
        net_movement_minor = total_credits_minor - total_debits_minor

        pending_reviews = db.query(Transaction).filter(
            Transaction.review_status == "NEEDS_REVIEW"
        ).count()

        anomalies_count = db.query(Transaction).filter(
            (Transaction.is_anomaly == True) | (Transaction.is_duplicate == True)
        ).count()

        reconciled_count = db.query(Statement).filter(
            Statement.reconciliation_status == "RECONCILED"
        ).count()

        return {
            "total_statements": stmt_count,
            "total_transactions": txn_count,
            "total_debits": float(FinancialNormalizer.to_decimal(total_debits_minor, 2)),
            "total_credits": float(FinancialNormalizer.to_decimal(total_credits_minor, 2)),
            "net_movement": float(FinancialNormalizer.to_decimal(net_movement_minor, 2)),
            "pending_reviews": pending_reviews,
            "anomalies_count": anomalies_count,
            "reconciled_statements": reconciled_count,
        }

    @classmethod
    def get_category_analytics(cls, db: Session, statement_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = db.query(
            Transaction.category,
            func.count(Transaction.id).label("count"),
            func.sum(Transaction.debit_minor).label("total_debit"),
            func.sum(Transaction.credit_minor).label("total_credit"),
        )
        if statement_id:
            query = query.filter(Transaction.statement_id == statement_id)

        rows = query.group_by(Transaction.category).all()
        total_debit_all = sum(r[2] or 0 for r in rows) or 1

        results = []
        for r in rows:
            cat_name = r[0]
            cnt = r[1]
            deb = r[2] or 0
            cred = r[3] or 0
            pct = round((deb / total_debit_all) * 100, 2)
            results.append({
                "category": cat_name,
                "count": cnt,
                "total_debit": float(FinancialNormalizer.to_decimal(deb, 2)),
                "total_credit": float(FinancialNormalizer.to_decimal(cred, 2)),
                "percentage_of_expense": pct,
            })

        results.sort(key=lambda x: x["total_debit"], reverse=True)
        return results

    @classmethod
    def get_cashflow(cls, db: Session, statement_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = db.query(
            Transaction.date,
            func.sum(Transaction.debit_minor).label("debits"),
            func.sum(Transaction.credit_minor).label("credits"),
            func.count(Transaction.id).label("count"),
        )
        if statement_id:
            query = query.filter(Transaction.statement_id == statement_id)

        rows = query.group_by(Transaction.date).order_by(Transaction.date.asc()).all()
        timeline = []
        for r in rows:
            d_amt = float(FinancialNormalizer.to_decimal(r[1] or 0, 2))
            c_amt = float(FinancialNormalizer.to_decimal(r[2] or 0, 2))
            timeline.append({
                "date": r[0],
                "debits": d_amt,
                "credits": c_amt,
                "net": round(c_amt - d_amt, 2),
                "count": r[3],
            })
        return timeline

    @classmethod
    def get_classification_distribution(cls, db: Session) -> List[Dict[str, Any]]:
        rows = db.query(
            Transaction.classification_method,
            func.count(Transaction.id)
        ).group_by(Transaction.classification_method).all()

        total = sum(r[1] for r in rows) or 1
        return [
            {
                "method": r[0],
                "count": r[1],
                "percentage": round((r[1] / total) * 100, 1),
            }
            for r in rows
        ]

