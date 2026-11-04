import re
from typing import List, Dict, Optional

class HeaderDetector:
    """Detects standard transaction table columns from arbitrary header row variations."""

    DATE_SYNONYMS = ["date", "txn date", "txndate", "transaction date", "value date", "post date", "trans date"]
    DESC_SYNONYMS = ["description", "narration", "particulars", "details", "transaction details", "remarks", "party name"]
    DEBIT_SYNONYMS = ["debit", "withdrawal", "withdrawal amount", "dr amount", "dr", "debit amount", "withdrawals"]
    CREDIT_SYNONYMS = ["credit", "deposit", "deposit amount", "cr amount", "cr", "credit amount", "deposits"]
    BALANCE_SYNONYMS = ["balance", "running balance", "available balance", "closing balance", "net balance", "balance (inr)"]
    AMOUNT_SYNONYMS = ["amount", "txn amount", "transaction amount"]

    @classmethod
    def match_header(cls, row: List[str]) -> Optional[Dict[str, int]]:
        """
        Analyzes a candidate table row and maps recognized column names to their 0-based indices.
        Returns a dict e.g. {'date': 0, 'desc': 1, 'debit': 2, 'credit': 3, 'balance': 4}
        or None if insufficient columns match.
        """
        normalized_row = [re.sub(r"[^\w\s]", "", c.lower().strip()) for c in row]
        mapping: Dict[str, int] = {}

        for idx, cell in enumerate(normalized_row):
            if not cell:
                continue

            if "date" not in mapping and any(syn == cell or syn in cell for syn in cls.DATE_SYNONYMS):
                mapping["date"] = idx
                continue

            if "desc" not in mapping and any(syn == cell or syn in cell for syn in cls.DESC_SYNONYMS):
                mapping["desc"] = idx
                continue

            if "debit" not in mapping and any(syn == cell or syn in cell for syn in cls.DEBIT_SYNONYMS):
                mapping["debit"] = idx
                continue

            if "credit" not in mapping and any(syn == cell or syn in cell for syn in cls.CREDIT_SYNONYMS):
                mapping["credit"] = idx
                continue

            if "balance" not in mapping and any(syn == cell or syn in cell for syn in cls.BALANCE_SYNONYMS):
                mapping["balance"] = idx
                continue

            if "amount" not in mapping and any(syn == cell or syn in cell for syn in cls.AMOUNT_SYNONYMS):
                mapping["amount"] = idx
                continue

        # Valid table header must at least have date, description, and either (debit/credit) or (amount)
        has_essential = "date" in mapping and "desc" in mapping and (("debit" in mapping or "credit" in mapping) or "amount" in mapping)
        if has_essential:
            return mapping
        return None
