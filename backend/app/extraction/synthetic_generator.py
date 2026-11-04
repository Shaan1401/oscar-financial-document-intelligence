import json
from pathlib import Path
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class SyntheticStatementGenerator:
    """Generates reproducible, realistic synthetic bank statements for testing and benchmarking."""

    @staticmethod
    def generate_layout_a(output_pdf_path: str | Path, ground_truth_json_path: str | Path):
        """
        Layout A: Conventional Separate Debit and Credit Columns.
        Fictional Bank: 'OSCAR Demonstration Bank'
        """
        output_pdf_path = Path(output_pdf_path)
        ground_truth_json_path = Path(ground_truth_json_path)

        doc = SimpleDocTemplate(
            str(output_pdf_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#1E3A8A"),
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "SubTitleStyle",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=12,
        )
        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
        )
        header_table_style = ParagraphStyle(
            "HeaderTableStyle",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#1E293B"),
        )

        story = []

        # 1. Bank Header & Watermark
        story.append(Paragraph("OSCAR DEMONSTRATION BANK", title_style))
        story.append(Paragraph("SYNTHETIC DEMONSTRATION STATEMENT — FOR SYSTEM VERIFICATION ONLY", subtitle_style))
        story.append(Spacer(1, 8))

        # 2. Account Information Block
        account_data = [
            [
                Paragraph("<b>Account Holder Name:</b> Rajesh Kumar Sharma", header_table_style),
                Paragraph("<b>Account Number:</b> 50100234891234", header_table_style),
            ],
            [
                Paragraph("<b>Customer ID:</b> CUST-893214", header_table_style),
                Paragraph("<b>IFSC Code:</b> OSCB0001234", header_table_style),
            ],
            [
                Paragraph("<b>Branch:</b> Connaught Place, New Delhi", header_table_style),
                Paragraph("<b>Currency:</b> INR", header_table_style),
            ],
            [
                Paragraph("<b>Statement Period:</b> 01/10/2026 to 15/10/2026", header_table_style),
                Paragraph("<b>Opening Balance:</b> ₹ 45,000.00", header_table_style),
            ],
        ]

        t_account = Table(account_data, colWidths=[270, 270])
        t_account.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_account)
        story.append(Spacer(1, 14))

        # 3. Transaction Records (Balanced & Internally Consistent)
        opening_balance = Decimal("45000.00")
        raw_txns = [
            {"date": "01/10/2026", "desc": "SALARY CREDIT - ACME TECH LABS PVT LTD", "debit": Decimal("0.00"), "credit": Decimal("85000.00")},
            {"date": "02/10/2026", "desc": "UPI/ZOMATO/ORDER-78932/FOOD", "debit": Decimal("480.00"), "credit": Decimal("0.00")},
            {"date": "03/10/2026", "desc": "SWIGGY BANGALORE IN/REST", "debit": Decimal("650.00"), "credit": Decimal("0.00")},
            {"date": "04/10/2026", "desc": "DMART SUPERMARKET RETAIL STORE", "debit": Decimal("3420.50"), "credit": Decimal("0.00")},
            {"date": "05/10/2026", "desc": "AMAZON PAY INDIA E-COMMERCE", "debit": Decimal("1899.00"), "credit": Decimal("0.00")},
            {"date": "06/10/2026", "desc": "UBER INDIA RIDES PVT LTD TRIP", "debit": Decimal("340.00"), "credit": Decimal("0.00")},
            {"date": "07/10/2026", "desc": "HPCL FUEL STATION PETROL PUMP", "debit": Decimal("2000.00"), "credit": Decimal("0.00")},
            {"date": "08/10/2026", "desc": "BESCOM ELECTRICITY BILL PAYMENT", "debit": Decimal("1450.00"), "credit": Decimal("0.00")},
            {"date": "09/10/2026", "desc": "APOLLO PHARMACY HEALTHCARE", "debit": Decimal("820.00"), "credit": Decimal("0.00")},
            {"date": "10/10/2026", "desc": "ATM CASH WDL HDFC ATM CONNAUGHT", "debit": Decimal("5000.00"), "credit": Decimal("0.00")},
            {"date": "11/10/2026", "desc": "NETFLIX ENTERTAINMENT SUBSCRIPTION", "debit": Decimal("649.00"), "credit": Decimal("0.00")},
            {"date": "12/10/2026", "desc": "ANNUAL SMS ALERT BANK CHARGES", "debit": Decimal("59.00"), "credit": Decimal("0.00")},
            {"date": "13/10/2026", "desc": "REFUND AMAZON PAY FAILED ORDER", "debit": Decimal("0.00"), "credit": Decimal("1899.00")},
            {"date": "14/10/2026", "desc": "IMPS/P2A/TRANSFER TO SISTER A/C", "debit": Decimal("10000.00"), "credit": Decimal("0.00")},
            {"date": "15/10/2026", "desc": "HDFC HOME LOAN AUTO DEBIT EMI", "debit": Decimal("22500.00"), "credit": Decimal("0.00")},
        ]

        table_rows = [
            ["Date", "Narration / Description", "Debit", "Credit", "Balance"]
        ]

        ground_truth_txns = []
        running_bal = opening_balance
        total_debits = Decimal("0.00")
        total_credits = Decimal("0.00")

        for idx, t in enumerate(raw_txns, 1):
            running_bal = running_bal + t["credit"] - t["debit"]
            total_debits += t["debit"]
            total_credits += t["credit"]

            table_rows.append([
                t["date"],
                Paragraph(t["desc"], body_style),
                f"{t['debit']:.2f}" if t["debit"] > 0 else "-",
                f"{t['credit']:.2f}" if t["credit"] > 0 else "-",
                f"{running_bal:.2f}",
            ])

            ground_truth_txns.append({
                "sequence": idx,
                "date": t["date"],
                "description": t["desc"],
                "debit": float(t["debit"]),
                "credit": float(t["credit"]),
                "balance": float(running_bal),
            })

        t_txns = Table(table_rows, colWidths=[65, 235, 75, 75, 90])
        t_txns.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        story.append(t_txns)
        story.append(Spacer(1, 14))

        # 4. Closing Balance & Totals Summary
        summary_data = [
            [
                Paragraph("<b>Total Debits:</b>", header_table_style),
                Paragraph(f"₹ {total_debits:.2f}", header_table_style),
                Paragraph("<b>Total Credits:</b>", header_table_style),
                Paragraph(f"₹ {total_credits:.2f}", header_table_style),
                Paragraph("<b>Closing Balance:</b>", header_table_style),
                Paragraph(f"₹ {running_bal:.2f}", header_table_style),
            ]
        ]
        t_summary = Table(summary_data, colWidths=[70, 100, 70, 100, 80, 120])
        t_summary.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF2F6")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("ALIGN", (3, 0), (3, 0), "RIGHT"),
            ("ALIGN", (5, 0), (5, 0), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t_summary)

        # Build document
        doc.build(story)

        # Save Ground Truth JSON
        ground_truth = {
            "metadata": {
                "bank_name": "OSCAR Demonstration Bank",
                "account_holder": "Rajesh Kumar Sharma",
                "account_number": "50100234891234",
                "ifsc_code": "OSCB0001234",
                "branch": "Connaught Place, New Delhi",
                "statement_period": "01/10/2026 to 15/10/2026",
                "opening_balance": float(opening_balance),
                "closing_balance": float(running_bal),
                "total_debits": float(total_debits),
                "total_credits": float(total_credits),
                "transaction_count": len(ground_truth_txns),
                "layout": "Layout A - Standard Separate Debit/Credit",
            },
            "transactions": ground_truth_txns,
        }

        with open(ground_truth_json_path, "w", encoding="utf-8") as f:
            json.dump(ground_truth, f, indent=2)

        return output_pdf_path, ground_truth_json_path
