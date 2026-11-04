import io
from decimal import Decimal
from typing import List
from datetime import datetime, timezone
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from app.database.models import Statement, Transaction, Account
from app.validation.normalizer import FinancialNormalizer

class ExcelExporter:
    """Generates a professional, multi-tab financial Excel workbook (.xlsx)."""

    NAVY_FILL = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    TITLE_FONT = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
    BOLD_FONT = Font(name="Calibri", size=11, bold=True)
    REGULAR_FONT = Font(name="Calibri", size=11)
    MUTED_FONT = Font(name="Calibri", size=9, italic=True, color="64748B")

    THIN_BORDER = Border(
        left=Side(style="thin", color="E2E8F0"),
        right=Side(style="thin", color="E2E8F0"),
        top=Side(style="thin", color="E2E8F0"),
        bottom=Side(style="thin", color="E2E8F0"),
    )

    ZEBRA_FILL = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    ALERT_FILL = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")

    @classmethod
    def export_statement(cls, statement: Statement, transactions: List[Transaction], account: Account = None) -> bytes:
        wb = openpyxl.Workbook()

        # ---------------- Sheet 1: Transactions ----------------
        ws_txn = wb.active
        ws_txn.title = "Transactions"
        ws_txn.views.sheetView[0].showGridLines = True

        headers = [
            "Date", "Description", "Debit", "Credit", "Balance", "Currency",
            "Category", "Classification Method", "Confidence Score", "Review Status",
            "Source Page", "Validation Warnings"
        ]

        # Header row
        for col_idx, h in enumerate(headers, 1):
            cell = ws_txn.cell(row=1, column=col_idx, value=h)
            cell.fill = cls.NAVY_FILL
            cell.font = cls.HEADER_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = cls.THIN_BORDER

        # Data rows
        for row_idx, txn in enumerate(transactions, 2):
            debit_dec = float(FinancialNormalizer.to_decimal(txn.debit_minor, txn.exponent))
            credit_dec = float(FinancialNormalizer.to_decimal(txn.credit_minor, txn.exponent))
            bal_dec = float(FinancialNormalizer.to_decimal(txn.balance_minor, txn.exponent)) if txn.balance_minor is not None else ""

            row_data = [
                txn.date,
                txn.description,
                debit_dec if debit_dec > 0 else 0.0,
                credit_dec if credit_dec > 0 else 0.0,
                bal_dec,
                txn.currency,
                txn.category,
                txn.classification_method,
                round(txn.confidence_score, 4) if txn.confidence_score is not None else "",
                txn.review_status,
                txn.source_page,
                txn.validation_warnings or "",
            ]

            is_zebra = (row_idx % 2 == 0)
            has_warning = bool(txn.validation_warnings or txn.review_status == "NEEDS_REVIEW")

            for col_idx, val in enumerate(row_data, 1):
                cell = ws_txn.cell(row=row_idx, column=col_idx, value=val)
                cell.font = cls.REGULAR_FONT
                cell.border = cls.THIN_BORDER

                if has_warning:
                    cell.fill = cls.ALERT_FILL
                elif is_zebra:
                    cell.fill = cls.ZEBRA_FILL

                # Format numbers
                if col_idx in [3, 4, 5] and isinstance(val, (int, float)):
                    cell.number_format = "#,##0.00"
                    cell.alignment = Alignment(horizontal="right")
                elif col_idx in [1, 6, 8, 9, 10, 11]:
                    cell.alignment = Alignment(horizontal="center")
                else:
                    cell.alignment = Alignment(horizontal="left")

        # Freeze top row and set auto-filter
        ws_txn.freeze_panes = "A2"
        ws_txn.auto_filter.ref = ws_txn.dimensions

        # Auto-adjust column widths
        cls._adjust_column_widths(ws_txn)

        # ---------------- Sheet 2: Account Summary ----------------
        ws_acc = wb.create_sheet(title="Account Summary")
        ws_acc.views.sheetView[0].showGridLines = True
        ws_acc.append(["OSCAR Financial Intelligence — Statement Account Summary"])
        ws_acc["A1"].font = cls.TITLE_FONT

        acc_details = [
            ("Bank Name", statement.bank_name or "Unknown"),
            ("Account Holder", account.holder_name if account else "Not Detected"),
            ("Account Number", account.masked_number if account else "Not Detected"),
            ("IFSC Code", account.ifsc_code if account else "Not Detected"),
            ("Branch", account.branch if account else "Not Detected"),
            ("Statement Period", statement.statement_period or f"{statement.start_date or 'N/A'} to {statement.end_date or 'N/A'}"),
            ("Currency", statement.currency),
            ("Document Pages", statement.page_count),
            ("Detected PDF Type", statement.pdf_type),
        ]

        ws_acc.append([])
        for label, val in acc_details:
            r = ws_acc.max_row + 1
            c1 = ws_acc.cell(row=r, column=1, value=label)
            c2 = ws_acc.cell(row=r, column=2, value=val)
            c1.font = cls.BOLD_FONT
            c2.font = cls.REGULAR_FONT
            c1.border = cls.THIN_BORDER
            c2.border = cls.THIN_BORDER
        cls._adjust_column_widths(ws_acc)

        # ---------------- Sheet 3: Reconciliation ----------------
        ws_rec = wb.create_sheet(title="Reconciliation")
        ws_rec.views.sheetView[0].showGridLines = True
        ws_rec.append(["Financial Reconciliation & Balance Validation"])
        ws_rec["A1"].font = cls.TITLE_FONT
        ws_rec.append([])

        op_bal = float(FinancialNormalizer.to_decimal(statement.opening_balance_minor, statement.exponent)) if statement.opening_balance_minor is not None else 0.0
        tot_cr = float(FinancialNormalizer.to_decimal(statement.total_credits_minor, statement.exponent))
        tot_dr = float(FinancialNormalizer.to_decimal(statement.total_debits_minor, statement.exponent))
        exp_cl = float(FinancialNormalizer.to_decimal(statement.expected_closing_minor, statement.exponent)) if statement.expected_closing_minor is not None else (op_bal + tot_cr - tot_dr)
        act_cl = float(FinancialNormalizer.to_decimal(statement.closing_balance_minor, statement.exponent)) if statement.closing_balance_minor is not None else 0.0
        variance = float(FinancialNormalizer.to_decimal(statement.variance_minor, statement.exponent)) if statement.variance_minor is not None else (act_cl - exp_cl)

        rec_metrics = [
            ("Opening Balance", op_bal),
            ("Total Credits (+)", tot_cr),
            ("Total Debits (-)", tot_dr),
            ("Expected Closing Balance", exp_cl),
            ("Actual Closing Balance", act_cl),
            ("Variance", variance),
            ("Reconciliation Status", statement.reconciliation_status),
        ]

        for label, val in rec_metrics:
            r = ws_rec.max_row + 1
            c1 = ws_rec.cell(row=r, column=1, value=label)
            c2 = ws_rec.cell(row=r, column=2, value=val)
            c1.font = cls.BOLD_FONT
            c2.font = cls.REGULAR_FONT
            c1.border = cls.THIN_BORDER
            c2.border = cls.THIN_BORDER
            if isinstance(val, (int, float)):
                c2.number_format = "#,##0.00"
                c2.alignment = Alignment(horizontal="right")
        cls._adjust_column_widths(ws_rec)

        # ---------------- Sheet 4: Processing Info ----------------
        ws_meta = wb.create_sheet(title="Audit Info")
        ws_meta.views.sheetView[0].showGridLines = True
        ws_meta.append(["OSCAR Processing & Provenance Metadata"])
        ws_meta["A1"].font = cls.TITLE_FONT
        ws_meta.append([])

        meta_rows = [
            ("Statement ID", statement.id),
            ("Source Filename", statement.filename),
            ("SHA-256 Checksum", statement.file_hash),
            ("Parsed Date", statement.created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if statement.created_at else "N/A"),
            ("Platform", "OSCAR — Financial Document Intelligence"),
            ("Export Timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")),
        ]
        for label, val in meta_rows:
            r = ws_meta.max_row + 1
            c1 = ws_meta.cell(row=r, column=1, value=label)
            c2 = ws_meta.cell(row=r, column=2, value=val)
            c1.font = cls.BOLD_FONT
            c2.font = cls.REGULAR_FONT
            c1.border = cls.THIN_BORDER
            c2.border = cls.THIN_BORDER
        cls._adjust_column_widths(ws_meta)

        out = io.BytesIO()
        wb.save(out)
        return out.getvalue()

    @staticmethod
    def _adjust_column_widths(ws):
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if "\n" in val_str:
                    val_str = max(val_str.split("\n"), key=len)
                max_len = max(max_len, len(val_str))
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 60)
