import csv
import io
from typing import List
from app.database.models import Transaction
from app.validation.normalizer import FinancialNormalizer

class CSVExporter:
    """Exports transactions to standardized CSV format with formula injection sanitization."""

    @classmethod
    def sanitize_field(cls, value: str) -> str:
        """
        Prevents CSV formula injection vulnerabilities.
        If a cell begins with '=', '+', '-', or '@', prepend a single quote.
        """
        if not value:
            return ""
        val = str(value)
        if val.startswith(("=", "+", "-", "@", "\t", "\r")):
            return f"'{val}"
        return val

    @classmethod
    def export_transactions(cls, transactions: List[Transaction]) -> str:
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Mandatory headers from assessment
        headers = [
            "Date",
            "Description",
            "Debit",
            "Credit",
            "Balance",
            "Currency",
            "Category",
            "Classification Method",
            "Confidence Score",
            "Review Status",
            "Source Page",
            "Row Sequence",
            "Validation Warnings",
        ]
        writer.writerow(headers)

        for txn in transactions:
            debit_val = FinancialNormalizer.to_decimal(txn.debit_minor, txn.exponent)
            credit_val = FinancialNormalizer.to_decimal(txn.credit_minor, txn.exponent)
            balance_val = (
                FinancialNormalizer.to_decimal(txn.balance_minor, txn.exponent)
                if txn.balance_minor is not None
                else ""
            )

            row = [
                cls.sanitize_field(txn.date),
                cls.sanitize_field(txn.description),
                f"{debit_val:.2f}" if debit_val > 0 else "0.00",
                f"{credit_val:.2f}" if credit_val > 0 else "0.00",
                f"{balance_val:.2f}" if balance_val != "" else "",
                txn.currency,
                cls.sanitize_field(txn.category),
                txn.classification_method,
                f"{txn.confidence_score:.4f}" if txn.confidence_score is not None else "",
                txn.review_status,
                str(txn.source_page),
                str(txn.row_sequence),
                cls.sanitize_field(txn.validation_warnings or ""),
            ]
            writer.writerow(row)

        return output.getvalue()
