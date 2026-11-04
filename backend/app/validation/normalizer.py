import re
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Optional, Tuple

class FinancialNormalizer:
    """Normalizes financial amounts, dates, and account text with strict precision."""

    # Regex to clean currency symbols, commas, spaces
    CLEAN_AMOUNT_REGEX = re.compile(r"[^\d.,\-+()a-zA-Z]")
    
    @staticmethod
    def to_minor_units(amount: Decimal | float | str | int, exponent: int = 2) -> int:
        """Converts an amount into integer minor units (e.g. 10.50 -> 1050)."""
        if amount is None:
            return 0
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        multiplier = Decimal(10 ** exponent)
        return int((amount * multiplier).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @staticmethod
    def to_decimal(minor_units: Optional[int], exponent: int = 2) -> Decimal:
        """Converts integer minor units back to Decimal (e.g. 1050 -> Decimal('10.50'))."""
        if minor_units is None:
            return Decimal("0.00")
        divisor = Decimal(10 ** exponent)
        return Decimal(minor_units) / divisor

    @classmethod
    def parse_amount(cls, raw: str) -> Tuple[Decimal, Optional[str]]:
        """
        Parses a raw financial string into a Decimal and any DR/CR indicator.
        Handles:
          - "₹ 1,450.50" -> (Decimal('1450.50'), None)
          - "1,200.00 Cr" -> (Decimal('1200.00'), 'CR')
          - "500.00 Dr" -> (Decimal('500.00'), 'DR')
          - "(750.25)" -> (Decimal('-750.25'), 'DR')
          - "-340.00" -> (Decimal('-340.00'), None)
        """
        if not raw or not isinstance(raw, str):
            return Decimal("0.00"), None

        text = raw.strip()
        indicator = None

        # Check for DR/CR suffixes or prefixes
        upper = text.upper()
        if "CR" in upper:
            indicator = "CR"
            text = re.sub(r"(?i)\bcr\b|\.cr", "", text)
        elif "DR" in upper:
            indicator = "DR"
            text = re.sub(r"(?i)\bdr\b|\.dr", "", text)

        # Check for parentheses indicating negative/debit
        is_parenthesized = False
        if text.startswith("(") and text.endswith(")"):
            is_parenthesized = True
            text = text[1:-1]

        # Strip currency symbols and whitespace
        text = cls.CLEAN_AMOUNT_REGEX.sub("", text).strip()
        if not text:
            return Decimal("0.00"), indicator

        # Standardize Indian & International commas: "1,25,000.50" or "125,000.50"
        # If commas exist and dot is decimal separator
        if "," in text and "." in text:
            text = text.replace(",", "")
        elif "," in text and "." not in text:
            # Check if comma was decimal separator or thousands separator
            parts = text.split(",")
            if len(parts[-1]) == 2:  # likely decimal comma: "1250,50"
                text = "".join(parts[:-1]) + "." + parts[-1]
            else:
                text = text.replace(",", "")

        try:
            val = Decimal(text)
            if is_parenthesized and val > 0:
                val = -val
            return val, indicator
        except Exception:
            return Decimal("0.00"), indicator

    @staticmethod
    def parse_date(raw_date: str) -> Tuple[str, bool]:
        """
        Parses various date formats into standardized ISO 'YYYY-MM-DD'.
        Returns (standardized_date_str, is_ambiguous).
        """
        if not raw_date or not isinstance(raw_date, str):
            return "", True

        cleaned = raw_date.strip()
        cleaned = re.sub(r"[^\w\s\-/.]", "", cleaned)

        formats = [
            ("%d/%m/%Y", False),
            ("%d-%m-%Y", False),
            ("%Y-%m-%d", False),
            ("%d/%m/%y", True),
            ("%d-%m-%y", True),
            ("%d %b %Y", False),
            ("%d-%b-%Y", False),
            ("%d %B %Y", False),
            ("%d-%B-%Y", False),
            ("%b %d, %Y", False),
            ("%m/%d/%Y", True),  # US style marked ambiguous
        ]

        for fmt, is_ambig in formats:
            try:
                dt = datetime.strptime(cleaned, fmt)
                return dt.strftime("%Y-%m-%d"), is_ambig
            except ValueError:
                continue

        return cleaned, True

    @staticmethod
    def mask_account_number(account_num: Optional[str]) -> str:
        """Masks an account number showing only the last 4 digits."""
        if not account_num:
            return "N/A"
        clean = re.sub(r"\s+", "", account_num)
        if len(clean) <= 4:
            return clean
        return "X" * (len(clean) - 4) + clean[-4:]

    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """Sanitizes transaction narration string."""
        if not text:
            return ""
        # Replace newlines, tabs and multiple whitespace with a single space
        return re.sub(r"\s+", " ", text).strip()
