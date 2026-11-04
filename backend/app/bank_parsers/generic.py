from typing import List, Dict, Any, Optional
from decimal import Decimal
from app.bank_parsers.base import BaseBankParser, ParsedTransaction
from app.bank_parsers.header_mapping import HeaderDetector
from app.validation.normalizer import FinancialNormalizer

class GenericBankParser(BaseBankParser):
    """
    Robust generic parser handling:
      - Separate debit/credit columns
      - Combined amount with DR/CR tags or signs
      - Wrapped / multiline narrative rows
      - Multi-page continuation
    """

    name: str = "GenericBankParser"
    layout_type: str = "generic"

    def can_parse(self, doc_data: Dict[str, Any]) -> float:
        """Checks if tables contain recognized column headers."""
        pages = doc_data.get("pages", [])
        for page in pages:
            for table in page.tables:
                for row in table[:5]:  # Look in first 5 rows
                    if HeaderDetector.match_header(row):
                        return 0.85
        return 0.20  # Fallback score

    def parse(self, doc_data: Dict[str, Any]) -> List[ParsedTransaction]:
        transactions: List[ParsedTransaction] = []
        pages = doc_data.get("pages", [])
        row_seq = 0

        current_header_mapping: Optional[Dict[str, int]] = None

        for page in pages:
            for table in page.tables:
                for row_idx, row in enumerate(table):
                    # Check if row is a header
                    mapping = HeaderDetector.match_header(row)
                    if mapping:
                        current_header_mapping = mapping
                        continue

                    if not current_header_mapping:
                        continue

                    # Extract raw cells safely
                    date_idx = current_header_mapping.get("date")
                    desc_idx = current_header_mapping.get("desc")
                    debit_idx = current_header_mapping.get("debit")
                    credit_idx = current_header_mapping.get("credit")
                    balance_idx = current_header_mapping.get("balance")
                    amount_idx = current_header_mapping.get("amount")

                    raw_date = row[date_idx].strip() if date_idx is not None and date_idx < len(row) else ""
                    raw_desc = row[desc_idx].strip() if desc_idx is not None and desc_idx < len(row) else ""
                    raw_debit = row[debit_idx].strip() if debit_idx is not None and debit_idx < len(row) else ""
                    raw_credit = row[credit_idx].strip() if credit_idx is not None and credit_idx < len(row) else ""
                    raw_balance = row[balance_idx].strip() if balance_idx is not None and balance_idx < len(row) else ""
                    raw_amount = row[amount_idx].strip() if amount_idx is not None and amount_idx < len(row) else ""

                    # Handle multiline continuation: if date is empty but we have a preceding transaction,
                    # append text to previous description
                    if not raw_date and raw_desc and transactions and not raw_debit and not raw_credit and not raw_amount:
                        prev = transactions[-1]
                        prev.description = FinancialNormalizer.clean_text(f"{prev.description} {raw_desc}")
                        prev.raw_description = f"{prev.raw_description}\n{raw_desc}"
                        continue

                    # If date is absent or row has no financial amounts, skip
                    if not raw_date:
                        continue

                    std_date, is_ambiguous = FinancialNormalizer.parse_date(raw_date)
                    warnings = "Ambiguous date format" if is_ambiguous else None

                    debit_val = Decimal("0.00")
                    credit_val = Decimal("0.00")
                    balance_val: Optional[Decimal] = None

                    # Parse amounts
                    if amount_idx is not None and (raw_amount or not (raw_debit or raw_credit)):
                        # Combined amount column
                        amt, indicator = FinancialNormalizer.parse_amount(raw_amount)
                        if indicator == "DR" or amt < 0:
                            debit_val = abs(amt)
                        elif indicator == "CR" or amt > 0:
                            credit_val = amt
                        else:
                            # If no indicator, check raw_desc or default to debit for expenses
                            debit_val = abs(amt)
                    else:
                        if raw_debit:
                            d_val, _ = FinancialNormalizer.parse_amount(raw_debit)
                            debit_val = abs(d_val)
                        if raw_credit:
                            c_val, _ = FinancialNormalizer.parse_amount(raw_credit)
                            credit_val = abs(c_val)

                    if raw_balance:
                        b_val, _ = FinancialNormalizer.parse_amount(raw_balance)
                        balance_val = b_val

                    # Validate that this is a meaningful financial transaction
                    if debit_val == 0 and credit_val == 0 and not raw_desc:
                        continue

                    row_seq += 1
                    clean_desc = FinancialNormalizer.clean_text(raw_desc) or "Unspecified Transaction"

                    transactions.append(ParsedTransaction(
                        date=std_date,
                        description=clean_desc,
                        raw_description=raw_desc,
                        debit=debit_val,
                        credit=credit_val,
                        balance=balance_val,
                        source_page=page.page_number,
                        row_sequence=row_seq,
                        extraction_method="digital_text" if page.page_type == "text" else page.page_type,
                        validation_warnings=warnings,
                    ))

        return transactions
