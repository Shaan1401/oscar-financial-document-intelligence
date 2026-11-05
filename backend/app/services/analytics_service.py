import re
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import Statement, Transaction
from app.validation.normalizer import FinancialNormalizer

class AnalyticsService:
    """Database-backed financial analytics and dashboard metrics calculation."""

    MERCHANT_PATTERNS = [
        ("Zomato", re.compile(r"\b(?:ZOMATO|ZOM)\b", re.I)),
        ("Swiggy", re.compile(r"\b(?:SWIGGY|SWIG)\b", re.I)),
        ("Amazon", re.compile(r"\b(?:AMAZON|AMZN)\b", re.I)),
        ("DMart", re.compile(r"\b(?:DMART|AVENUE SUPERMARTS)\b", re.I)),
        ("Uber", re.compile(r"\b(?:UBER)\b", re.I)),
        ("Ola", re.compile(r"\b(?:OLA CABS|ANI TECH)\b", re.I)),
        ("HPCL Petrol", re.compile(r"\b(?:HPCL|HINDUSTAN PETROLEUM)\b", re.I)),
        ("BPCL Petrol", re.compile(r"\b(?:BPCL|BHARAT PETROLEUM)\b", re.I)),
        ("IOCL Petrol", re.compile(r"\b(?:IOCL|INDIAN OIL)\b", re.I)),
        ("Apollo Pharmacy", re.compile(r"\b(?:APOLLO|APOLLOPHARM)\b", re.I)),
        ("Netflix", re.compile(r"\b(?:NETFLIX)\b", re.I)),
        ("Hotstar / Disney", re.compile(r"\b(?:HOTSTAR|DISNEY)\b", re.I)),
        ("Spotify", re.compile(r"\b(?:SPOTIFY)\b", re.I)),
        ("Airtel", re.compile(r"\b(?:AIRTEL|BHARTI AIRTEL)\b", re.I)),
        ("Jio", re.compile(r"\b(?:JIO|RELIANCE JIO)\b", re.I)),
        ("Tata Services / TCS", re.compile(r"\b(?:TATA|TCS)\b", re.I)),
        ("Infosys", re.compile(r"\b(?:INFOSYS|INFY)\b", re.I)),
        ("Flipkart", re.compile(r"\b(?:FLIPKART|FKART)\b", re.I)),
        ("BigBasket", re.compile(r"\b(?:BIGBASKET|INNOVATIVE RETAIL)\b", re.I)),
        ("Blinkit", re.compile(r"\b(?:BLINKIT|GROFERS)\b", re.I)),
        ("BESCOM Electricity", re.compile(r"\b(?:BESCOM|ELECTRICITY)\b", re.I)),
        ("MakeMyTrip", re.compile(r"\b(?:MAKEMYTRIP|MMT)\b", re.I)),
        ("IRCTC Railway", re.compile(r"\b(?:IRCTC)\b", re.I)),
        ("HDFC Loan / EMI", re.compile(r"\b(?:HDFC HOME LOAN|HDFC LOAN)\b", re.I)),
        ("ICICI Loan / EMI", re.compile(r"\b(?:ICICI LOAN|ICICI BANK LOAN)\b", re.I)),
    ]

    CHANNEL_PATTERNS = [
        ("UPI", re.compile(r"\b(?:UPI|VPA|GPAY|PHONEPE|PAYTM)\b", re.I)),
        ("NEFT", re.compile(r"\b(?:NEFT)\b", re.I)),
        ("IMPS", re.compile(r"\b(?:IMPS|P2A|P2P)\b", re.I)),
        ("RTGS", re.compile(r"\b(?:RTGS)\b", re.I)),
        ("ATM / Cash", re.compile(r"\b(?:ATM|CASH WDL|NWD|ATW)\b", re.I)),
        ("POS / Card", re.compile(r"\b(?:POS|EDC|CARD|VISA|MASTERCARD|RUPAY)\b", re.I)),
        ("ECS / NACH / Mandate", re.compile(r"\b(?:ECS|ACH|NACH|AUTO DEBIT|MANDATE)\b", re.I)),
        ("Banking Charges / Interest", re.compile(r"\b(?:CHG|FEE|INTEREST|INT\.|ANNUAL SMS)\b", re.I)),
    ]

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
            Transaction.review_status.notin_(["APPROVED", "CORRECTED"]),
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

    @classmethod
    def get_running_balance_trajectory(cls, db: Session, statement_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculates running balance movements and identifies discrepancies along statement chronology."""
        if not statement_id:
            first_stmt = db.query(Statement).order_by(Statement.created_at.desc()).first()
            if not first_stmt:
                return {"statement_id": None, "opening_balance": 0.0, "closing_balance": 0.0, "currency": "INR", "points": []}
            stmt = first_stmt
        else:
            stmt = db.query(Statement).filter(Statement.id == statement_id).first()
            if not stmt:
                return {"statement_id": None, "opening_balance": 0.0, "closing_balance": 0.0, "currency": "INR", "points": []}

        txns = db.query(Transaction).filter(Transaction.statement_id == stmt.id).order_by(Transaction.row_sequence.asc()).all()
        exp = stmt.exponent
        op_bal = float(FinancialNormalizer.to_decimal(stmt.opening_balance_minor, exp)) if stmt.opening_balance_minor is not None else 0.0
        cl_bal = float(FinancialNormalizer.to_decimal(stmt.closing_balance_minor, exp)) if stmt.closing_balance_minor is not None else 0.0

        points = []
        current_running = op_bal
        for t in txns:
            deb = float(FinancialNormalizer.to_decimal(t.debit_minor, exp))
            cred = float(FinancialNormalizer.to_decimal(t.credit_minor, exp))
            bal = float(FinancialNormalizer.to_decimal(t.balance_minor, exp)) if t.balance_minor is not None else round(current_running + cred - deb, 2)
            current_running = bal

            points.append({
                "sequence": t.row_sequence,
                "date": t.date,
                "description": t.description,
                "debit": deb,
                "credit": cred,
                "balance": bal,
                "net_change": round(cred - deb, 2),
                "is_negative": bal < 0,
                "is_anomaly": bool(t.is_anomaly),
                "validation_status": t.validation_status,
                "validation_warnings": t.validation_warnings,
            })

        return {
            "statement_id": stmt.id,
            "filename": stmt.filename,
            "bank_name": stmt.bank_name,
            "currency": stmt.currency,
            "opening_balance": op_bal,
            "closing_balance": cl_bal,
            "points": points,
        }

    @classmethod
    def get_activity_heatmap(cls, db: Session, statement_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Calculates transaction density and volume across calendar dates."""
        query = db.query(
            Transaction.date,
            func.count(Transaction.id).label("count"),
            func.sum(Transaction.debit_minor).label("debits"),
            func.sum(Transaction.credit_minor).label("credits"),
        )
        if statement_id:
            query = query.filter(Transaction.statement_id == statement_id)

        rows = query.group_by(Transaction.date).order_by(Transaction.date.asc()).all()
        dates_list = []
        for r in rows:
            d_amt = float(FinancialNormalizer.to_decimal(r[2] or 0, 2))
            c_amt = float(FinancialNormalizer.to_decimal(r[3] or 0, 2))
            dates_list.append({
                "date": r[0],
                "count": r[1],
                "debits": d_amt,
                "credits": c_amt,
                "total_volume": round(d_amt + c_amt, 2),
                "net": round(c_amt - d_amt, 2),
            })
        return dates_list

    @classmethod
    def get_merchant_concentration(cls, db: Session, statement_id: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Identifies verified merchant entities and computes Pareto concentration."""
        query = db.query(Transaction)
        if statement_id:
            query = query.filter(Transaction.statement_id == statement_id)

        txns = query.all()
        merchant_spend: Dict[str, float] = {}
        merchant_count: Dict[str, int] = {}
        total_tracked = 0.0

        for t in txns:
            if t.debit_minor <= 0:
                continue
            amt = float(FinancialNormalizer.to_decimal(t.debit_minor, t.exponent))
            total_tracked += amt

            matched = False
            for m_name, pattern in cls.MERCHANT_PATTERNS:
                if pattern.search(t.description) or pattern.search(t.raw_description):
                    merchant_spend[m_name] = merchant_spend.get(m_name, 0.0) + amt
                    merchant_count[m_name] = merchant_count.get(m_name, 0) + 1
                    matched = True
                    break

            if not matched:
                merchant_spend["Other / Miscellaneous"] = merchant_spend.get("Other / Miscellaneous", 0.0) + amt
                merchant_count["Other / Miscellaneous"] = merchant_count.get("Other / Miscellaneous", 0) + 1

        # Sort descending by spend
        sorted_merchants = sorted(merchant_spend.items(), key=lambda x: x[1], reverse=True)
        items = []
        cum_spend = 0.0
        for m_name, spend in sorted_merchants[:limit]:
            cum_spend += spend
            pct = round((spend / total_tracked * 100), 2) if total_tracked > 0 else 0.0
            cum_pct = round((cum_spend / total_tracked * 100), 2) if total_tracked > 0 else 0.0
            items.append({
                "merchant": m_name,
                "amount": round(spend, 2),
                "count": merchant_count.get(m_name, 0),
                "percentage": pct,
                "cumulative_percentage": min(cum_pct, 100.0),
            })

        return {
            "total_tracked_spending": round(total_tracked, 2),
            "top_merchants": items,
        }

    @classmethod
    def get_payment_channels(cls, db: Session, statement_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Groups transactions into verified financial transfer and payment channels."""
        query = db.query(Transaction)
        if statement_id:
            query = query.filter(Transaction.statement_id == statement_id)

        txns = query.all()
        channel_data: Dict[str, Dict[str, Any]] = {}
        total_vol = 0.0

        for t in txns:
            amt = float(FinancialNormalizer.to_decimal(t.debit_minor + t.credit_minor, t.exponent))
            total_vol += amt

            matched = False
            for ch_name, pattern in cls.CHANNEL_PATTERNS:
                if pattern.search(t.description) or pattern.search(t.raw_description):
                    if ch_name not in channel_data:
                        channel_data[ch_name] = {"count": 0, "amount": 0.0}
                    channel_data[ch_name]["count"] += 1
                    channel_data[ch_name]["amount"] += amt
                    matched = True
                    break

            if not matched:
                if "Direct Transfer / Other" not in channel_data:
                    channel_data["Direct Transfer / Other"] = {"count": 0, "amount": 0.0}
                channel_data["Direct Transfer / Other"]["count"] += 1
                channel_data["Direct Transfer / Other"]["amount"] += amt

        results = []
        for ch, data in sorted(channel_data.items(), key=lambda x: x[1]["amount"], reverse=True):
            pct = round((data["amount"] / total_vol * 100), 2) if total_vol > 0 else 0.0
            results.append({
                "channel": ch,
                "count": data["count"],
                "total_amount": round(data["amount"], 2),
                "percentage": pct,
            })
        return results

    @classmethod
    def get_classification_deep(cls, db: Session) -> Dict[str, Any]:
        """Provides in-depth breakdown of rule engine vs traditional ML classification."""
        total = db.query(Transaction).count()
        rule_count = db.query(Transaction).filter(Transaction.classification_method == "RULE_BASED").count()
        ml_count = db.query(Transaction).filter(Transaction.classification_method == "MACHINE_LEARNING").count()
        manual_count = db.query(Transaction).filter(Transaction.classification_method == "MANUAL").count()
        review_count = db.query(Transaction).filter(Transaction.review_status == "NEEDS_REVIEW").count()

        # Score distribution bins: [0.0-0.5, 0.5-0.65, 0.65-0.80, 0.80-0.95, 0.95-1.0]
        bins = [
            {"range": "< 0.50 (Uncertain)", "min": 0.0, "max": 0.50, "count": 0},
            {"range": "0.50 - 0.65 (Gated Review)", "min": 0.50, "max": 0.65, "count": 0},
            {"range": "0.65 - 0.80 (Standard ML)", "min": 0.65, "max": 0.80, "count": 0},
            {"range": "0.80 - 0.95 (High Conf ML)", "min": 0.80, "max": 0.95, "count": 0},
            {"range": "0.95 - 1.00 (Rule / Exact)", "min": 0.95, "max": 1.01, "count": 0},
        ]

        txns = db.query(Transaction.confidence_score).all()
        for t in txns:
            sc = t[0] if t[0] is not None else 0.99
            for b in bins:
                if b["min"] <= sc < b["max"]:
                    b["count"] += 1
                    break

        for b in bins:
            b["percentage"] = round((b["count"] / total * 100), 1) if total > 0 else 0.0

        return {
            "total_transactions": total,
            "rule_based_count": rule_count,
            "rule_based_percentage": round((rule_count / total * 100), 1) if total > 0 else 0.0,
            "ml_based_count": ml_count,
            "ml_based_percentage": round((ml_count / total * 100), 1) if total > 0 else 0.0,
            "manual_count": manual_count,
            "needs_review_count": review_count,
            "score_distribution": bins,
        }

    @classmethod
    def get_extraction_completeness(cls, db: Session, statement_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculates field presence and structural completeness across extracted transactions."""
        query = db.query(Transaction)
        if statement_id:
            query = query.filter(Transaction.statement_id == statement_id)

        txns = query.all()
        total = len(txns)
        if total == 0:
            return {
                "total_records": 0,
                "date_completeness_pct": 100.0,
                "description_completeness_pct": 100.0,
                "amount_completeness_pct": 100.0,
                "balance_completeness_pct": 100.0,
                "coordinates_completeness_pct": 100.0,
                "overall_completeness_pct": 100.0,
            }

        date_cnt = sum(1 for t in txns if t.date and len(t.date.strip()) > 0)
        desc_cnt = sum(1 for t in txns if t.description and len(t.description.strip()) > 0)
        amt_cnt = sum(1 for t in txns if (t.debit_minor > 0 or t.credit_minor > 0))
        bal_cnt = sum(1 for t in txns if t.balance_minor is not None)
        coord_cnt = sum(1 for t in txns if t.source_page is not None)

        d_pct = round(date_cnt / total * 100, 1)
        desc_pct = round(desc_cnt / total * 100, 1)
        amt_pct = round(amt_cnt / total * 100, 1)
        bal_pct = round(bal_cnt / total * 100, 1)
        c_pct = round(coord_cnt / total * 100, 1)
        overall = round((d_pct + desc_pct + amt_pct + bal_pct + c_pct) / 5.0, 1)

        return {
            "total_records": total,
            "date_completeness_pct": d_pct,
            "description_completeness_pct": desc_pct,
            "amount_completeness_pct": amt_pct,
            "balance_completeness_pct": bal_pct,
            "coordinates_completeness_pct": c_pct,
            "overall_completeness_pct": overall,
        }

    @classmethod
    def get_multi_statement_comparison(cls, db: Session) -> Dict[str, Any]:
        """Compares distinct statements grouped strictly by currency without cross-currency contamination."""
        stmts = db.query(Statement).order_by(Statement.created_at.desc()).all()
        by_currency: Dict[str, List[Dict[str, Any]]] = {}

        for s in stmts:
            curr = s.currency or "INR"
            if curr not in by_currency:
                by_currency[curr] = []

            exp = s.exponent
            op = float(FinancialNormalizer.to_decimal(s.opening_balance_minor, exp)) if s.opening_balance_minor is not None else 0.0
            cl = float(FinancialNormalizer.to_decimal(s.closing_balance_minor, exp)) if s.closing_balance_minor is not None else 0.0
            dr = float(FinancialNormalizer.to_decimal(s.total_debits_minor, exp))
            cr = float(FinancialNormalizer.to_decimal(s.total_credits_minor, exp))

            by_currency[curr].append({
                "statement_id": s.id,
                "filename": s.filename,
                "bank_name": s.bank_name or "Standard Bank",
                "statement_period": s.statement_period or "N/A",
                "opening_balance": op,
                "total_credits": cr,
                "total_debits": dr,
                "net_movement": round(cr - dr, 2),
                "closing_balance": cl,
                "reconciliation_status": s.reconciliation_status,
                "transaction_count": len(s.transactions),
            })

        return {"by_currency": by_currency}

    @classmethod
    def get_category_trends(cls, db: Session, statement_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Provides chronological spend distribution grouped by category for trend visualization."""
        query = db.query(Transaction)
        if statement_id:
            query = query.filter(Transaction.statement_id == statement_id)

        txns = query.order_by(Transaction.date.asc()).all()
        # Collect top 6 categories
        cats = [
            "Food & Dining", "Groceries", "Shopping", "Transportation & Fuel",
            "Utilities", "Healthcare", "Salary & Income", "Transfers"
        ]

        # Group by date
        date_map: Dict[str, Dict[str, float]] = {}
        for t in txns:
            d = t.date
            if not d:
                continue
            if d not in date_map:
                date_map[d] = {c: 0.0 for c in cats}
                date_map[d]["date"] = d
                date_map[d]["total_debit"] = 0.0
                date_map[d]["total_credit"] = 0.0

            amt_deb = float(FinancialNormalizer.to_decimal(t.debit_minor, t.exponent))
            amt_cred = float(FinancialNormalizer.to_decimal(t.credit_minor, t.exponent))
            date_map[d]["total_debit"] += amt_deb
            date_map[d]["total_credit"] += amt_cred

            if t.category in cats:
                date_map[d][t.category] += amt_deb

        results = list(date_map.values())
        results.sort(key=lambda x: str(x["date"]))
        return results

