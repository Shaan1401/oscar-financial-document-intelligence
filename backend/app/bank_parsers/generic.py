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
            table_bboxes = getattr(page, "table_bboxes", [])
            for t_idx, table in enumerate(page.tables):
                bboxes = table_bboxes[t_idx] if t_idx < len(table_bboxes) else []
                for row_idx, row in enumerate(table):
                    row_bbox = bboxes[row_idx] if row_idx < len(bboxes) else None

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
                        if row_bbox and prev.bounding_box:
                            try:
                                p_parts = [float(x) for x in prev.bounding_box.split(",")]
                                r_parts = [float(x) for x in row_bbox.split(",")]
                                if len(p_parts) >= 4 and len(r_parts) >= 4:
                                    min_x0 = min(p_parts[0], r_parts[0])
                                    min_y0 = min(p_parts[1], r_parts[1])
                                    max_x1 = max(p_parts[2], r_parts[2])
                                    max_y1 = max(p_parts[3], r_parts[3])
                                    pw = p_parts[4] if len(p_parts) > 4 else 612.0
                                    ph = p_parts[5] if len(p_parts) > 5 else 792.0
                                    prev.bounding_box = f"{min_x0:.1f},{min_y0:.1f},{max_x1:.1f},{max_y1:.1f},{pw:.1f},{ph:.1f}"
                            except Exception:
                                pass
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
                    is_ocr = page.page_type == "scanned" or getattr(page, "ocr_status", None) == "SUCCESS"
                    ext_method = "ocr" if is_ocr else ("pdfplumber_table" if row_bbox else "digital_text")

                    transactions.append(ParsedTransaction(
                        date=std_date,
                        description=clean_desc,
                        raw_description=raw_desc,
                        debit=debit_val,
                        credit=credit_val,
                        balance=balance_val,
                        source_page=page.page_number,
                        row_sequence=row_seq,
                        bounding_box=row_bbox,
                        extraction_method=ext_method,
                        validation_warnings=warnings,
                    ))

        return transactions
