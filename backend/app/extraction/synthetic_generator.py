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

    @staticmethod
    def generate_layout_b(output_pdf_path: str | Path, ground_truth_json_path: str | Path):
        """
        Layout B: Combined Amount Column with 'DR' / 'CR' indicators.
        Fictional Bank: 'OSCAR Commercial Bank' (ICICI/Axis style layout).
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
            "TitleStyleB",
            parent=styles["Heading1"],
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#7C2D12"),  # Warm amber/brown
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "SubTitleStyleB",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#78716C"),
            spaceAfter=10,
        )
        body_style = ParagraphStyle(
            "BodyStyleB",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
        )
        header_table_style = ParagraphStyle(
            "HeaderTableStyleB",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#292524"),
        )

        story = []

        # 1. Header
        story.append(Paragraph("OSCAR COMMERCIAL BANK", title_style))
        story.append(Paragraph("SYNTHETIC DEMONSTRATION STATEMENT — COMBINED AMOUNT (DR/CR) LAYOUT", subtitle_style))
        story.append(Spacer(1, 6))

        # 2. Account Details Block
        account_data = [
            [
                Paragraph("<b>Account Holder:</b> Priya Sundaram", header_table_style),
                Paragraph("<b>Account No:</b> 918020045678912", header_table_style),
            ],
            [
                Paragraph("<b>Customer ID:</b> CORP-449120", header_table_style),
                Paragraph("<b>IFSC Code:</b> OCBL0004567", header_table_style),
            ],
            [
                Paragraph("<b>Branch:</b> Indiranagar, Bengaluru", header_table_style),
                Paragraph("<b>Currency:</b> INR", header_table_style),
            ],
            [
                Paragraph("<b>Period:</b> 01/10/2026 to 15/10/2026", header_table_style),
                Paragraph("<b>Opening Balance:</b> ₹ 72,500.00", header_table_style),
            ],
        ]

        t_account = Table(account_data, colWidths=[270, 270])
        t_account.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFBEB")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#FDE68A")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FEF3C7")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_account)
        story.append(Spacer(1, 12))

        # 3. Transactions with Combined Amount Column
        opening_balance = Decimal("72500.00")
        raw_txns = [
            {"date": "01/10/2026", "desc": "NEFT CR-INFOSYS BPO TECH CONSULTING-SALARY", "amount": Decimal("110000.00"), "type": "CR"},
            {"date": "02/10/2026", "desc": "UPI-SWIGGY FOOD DELIVERY-DELHI", "amount": Decimal("540.00"), "type": "DR"},
            {"date": "03/10/2026", "desc": "POS DEBIT-RELIANCE SMART SUPERSTORE", "amount": Decimal("4250.00"), "type": "DR"},
            {"date": "05/10/2026", "desc": "UPI-FLIPKART INTERNET PVT LTD ELECTRONICS", "amount": Decimal("12999.00"), "type": "DR"},
            {"date": "07/10/2026", "desc": "BILLDESK TANGEDCO POWER ELECTRICITY BILL", "amount": Decimal("2340.00"), "type": "DR"},
            {"date": "08/10/2026", "desc": "OLA CABS AUTO RIDE FARE CHARGES", "amount": Decimal("285.00"), "type": "DR"},
            {"date": "10/10/2026", "desc": "UPI-APOLLO CLINIC CONSULTATION & MEDS", "amount": Decimal("1250.00"), "type": "DR"},
            {"date": "11/10/2026", "desc": "ATM WDL-AXIS BANK ATM KORAMANGALA", "amount": Decimal("10000.00"), "type": "DR"},
            {"date": "12/10/2026", "desc": "MONTHLY MAINTENANCE CHARGES & GST", "amount": Decimal("177.00"), "type": "DR"},
            {"date": "13/10/2026", "desc": "CR-REFUND FLIPKART RETURN ORDER", "amount": Decimal("3499.00"), "type": "CR"},
            {"date": "14/10/2026", "desc": "IMPS OUT-FATHER MEDICAL SUPPORT TRANSFER", "amount": Decimal("15000.00"), "type": "DR"},
            {"date": "15/10/2026", "desc": "ICICI PRUDENTIAL LIFE INSURANCE PREMIUM", "amount": Decimal("8500.00"), "type": "DR"},
        ]

        table_rows = [
            ["Txn Date", "Transaction Details", "Txn Amount", "Balance"]
        ]

        ground_truth_txns = []
        running_bal = opening_balance
        total_debits = Decimal("0.00")
        total_credits = Decimal("0.00")

        for idx, t in enumerate(raw_txns, 1):
            if t["type"] == "CR":
                running_bal += t["amount"]
                total_credits += t["amount"]
                debit_amt = Decimal("0.00")
                credit_amt = t["amount"]
                amt_str = f"{t['amount']:.2f} CR"
            else:
                running_bal -= t["amount"]
                total_debits += t["amount"]
                debit_amt = t["amount"]
                credit_amt = Decimal("0.00")
                amt_str = f"{t['amount']:.2f} DR"

            table_rows.append([
                t["date"],
                Paragraph(t["desc"], body_style),
                amt_str,
                f"{running_bal:.2f}",
            ])

            ground_truth_txns.append({
                "sequence": idx,
                "date": t["date"],
                "description": t["desc"],
                "debit": float(debit_amt),
                "credit": float(credit_amt),
                "balance": float(running_bal),
            })

        t_txns = Table(table_rows, colWidths=[75, 275, 95, 95])
        t_txns.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7C2D12")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E7E5E4")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAF9")]),
        ]))
        story.append(t_txns)
        story.append(Spacer(1, 12))

        # 4. Summary
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
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#F59E0B")),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("ALIGN", (3, 0), (3, 0), "RIGHT"),
            ("ALIGN", (5, 0), (5, 0), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t_summary)

        doc.build(story)

        # Save Ground Truth JSON
        ground_truth = {
            "metadata": {
                "bank_name": "OSCAR Commercial Bank",
                "account_holder": "Priya Sundaram",
                "account_number": "918020045678912",
                "ifsc_code": "OCBL0004567",
                "branch": "Indiranagar, Bengaluru",
                "statement_period": "01/10/2026 to 15/10/2026",
                "opening_balance": float(opening_balance),
                "closing_balance": float(running_bal),
                "total_debits": float(total_debits),
                "total_credits": float(total_credits),
                "transaction_count": len(ground_truth_txns),
                "layout": "Layout B - Combined Amount with DR/CR Indicators",
            },
            "transactions": ground_truth_txns,
        }

        with open(ground_truth_json_path, "w", encoding="utf-8") as f:
            json.dump(ground_truth, f, indent=2)

        return output_pdf_path, ground_truth_json_path

    @staticmethod
    def generate_layout_c(output_pdf_path: str | Path, ground_truth_json_path: str | Path):
        """
        Layout C: Multi-Page Statement with Alternate Column Names and Wrapped Descriptions.
        Fictional Bank: 'OSCAR Premier Bank' (SBI/HDFC multi-page style).
        Headers: 'Value Date', 'Particulars', 'Withdrawals', 'Deposits', 'Net Balance'.
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
            "TitleStyleC",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#065F46"),  # Emerald green
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "SubTitleStyleC",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#047857"),
            spaceAfter=10,
        )
        body_style = ParagraphStyle(
            "BodyStyleC",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=9.5,
        )
        header_table_style = ParagraphStyle(
            "HeaderTableStyleC",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#064E3B"),
        )

        story = []

        # Page 1 Header
        story.append(Paragraph("OSCAR PREMIER BANK", title_style))
        story.append(Paragraph("OFFICIAL ACCOUNT STATEMENT — MULTI-PAGE ENTERPRISE SUMMARY", subtitle_style))
        story.append(Spacer(1, 6))

        account_data = [
            [
                Paragraph("<b>Account Holder Name:</b> Vikramaditya Singhania", header_table_style),
                Paragraph("<b>Account Number:</b> 330491028374", header_table_style),
            ],
            [
                Paragraph("<b>Customer ID:</b> PRM-992014", header_table_style),
                Paragraph("<b>IFSC Code:</b> OPBL0009988", header_table_style),
            ],
            [
                Paragraph("<b>Branch Name:</b> Bandra Kurla Complex, Mumbai", header_table_style),
                Paragraph("<b>Currency:</b> INR", header_table_style),
            ],
            [
                Paragraph("<b>Statement Period:</b> 01/10/2026 to 25/10/2026", header_table_style),
                Paragraph("<b>Opening Balance:</b> ₹ 1,50,000.00", header_table_style),
            ],
        ]

        t_account = Table(account_data, colWidths=[270, 270])
        t_account.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#A7F3D0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1FAE5")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_account)
        story.append(Spacer(1, 12))

        opening_balance = Decimal("150000.00")
        raw_txns = [
            # Page 1 Transactions
            {"date": "01/10/2026", "desc": "SALARY CREDIT - TATA CONSULTANCY SERVICES CORP ACCOUNTS", "debit": Decimal("0.00"), "credit": Decimal("175000.00")},
            {"date": "02/10/2026", "desc": "UPI/ZOMATO RESTAURANT DINING ORDER REF 902348 MUMBAI", "debit": Decimal("1420.00"), "credit": Decimal("0.00")},
            {"date": "03/10/2026", "desc": "DMART HYPERMARKET GROCERY PROVISIONS BANDRA WEST", "debit": Decimal("6780.00"), "credit": Decimal("0.00")},
            {"date": "05/10/2026", "desc": "AMAZON ONLINE SHOPPING INDIA FESTIVE PROMOTION ELECTRONICS", "debit": Decimal("4850.00"), "credit": Decimal("0.00")},
            {"date": "06/10/2026", "desc": "UBER INDIA COMMUTE PREMIUM SEDAN AIRPORT TRANSFER", "debit": Decimal("1120.00"), "credit": Decimal("0.00")},
            {"date": "07/10/2026", "desc": "MAHAVITARAN ELECTRICITY POWER DISTRIBUTION BOARD BILL", "debit": Decimal("3890.00"), "credit": Decimal("0.00")},
            {"date": "08/10/2026", "desc": "MAX HEALTHCARE SPECIALIST CLINIC DIAGNOSTIC TESTS", "debit": Decimal("2450.00"), "credit": Decimal("0.00")},
            {"date": "10/10/2026", "desc": "HOUSE RENT TRANSFER TO MR KISHORE SHARMA VIA NEFT", "debit": Decimal("45000.00"), "credit": Decimal("0.00")},
            {"date": "11/10/2026", "desc": "DPS INTERNATIONAL SCHOOL QUARTERLY TUITION FEES PAYMENT", "debit": Decimal("32000.00"), "credit": Decimal("0.00")},
            {"date": "12/10/2026", "desc": "PVR CINEMAS IMAX BANDRA ENTERTAINMENT TICKETS AND SNACKS", "debit": Decimal("1850.00"), "credit": Decimal("0.00")},
            {"date": "13/10/2026", "desc": "MAKEMYTRIP INDIA AIRLINE FLIGHT TICKETS BOOKING MUMBAI-DELHI", "debit": Decimal("14500.00"), "credit": Decimal("0.00")},
            {"date": "14/10/2026", "desc": "STAR HEALTH INSURANCE ANNUAL COMPREHENSIVE FAMILY POLICY", "debit": Decimal("18900.00"), "credit": Decimal("0.00")},
            {"date": "15/10/2026", "desc": "ZERODHA BROKING LTD MONTHLY MUTUAL FUND SIP INVESTMENT", "debit": Decimal("25000.00"), "credit": Decimal("0.00")},
            # Page Break will occur here
            {"date": "16/10/2026", "desc": "ATM CASH WITHDRAWAL PREMIER BANK ATM BRANCH BKC", "debit": Decimal("10000.00"), "credit": Decimal("0.00")},
            {"date": "17/10/2026", "desc": "QUARTERLY DEBIT CARD ANNUAL CHARGES & SERVICE TAX", "debit": Decimal("295.00"), "credit": Decimal("0.00")},
            {"date": "18/10/2026", "desc": "REFUND AMAZON PAY CANCELLED ITEM CREDIT PROCESSED", "debit": Decimal("0.00"), "credit": Decimal("4850.00")},
            {"date": "20/10/2026", "desc": "IMPS/TRANSFER TO YOUNGER BROTHER COLLEGE EXPENSES", "debit": Decimal("15000.00"), "credit": Decimal("0.00")},
            {"date": "22/10/2026", "desc": "HDFC CAR LOAN MONTHLY EMI AUTO RECOVERY REVENUE", "debit": Decimal("16500.00"), "credit": Decimal("0.00")},
            {"date": "24/10/2026", "desc": "INCOME TAX SELF ASSESSMENT TAX CHALLAN 280 PAYMENT", "debit": Decimal("22000.00"), "credit": Decimal("0.00")},
            {"date": "25/10/2026", "desc": "INTEREST CREDIT QUARTERLY SAVINGS BANK REVENUE", "debit": Decimal("0.00"), "credit": Decimal("1875.00")},
        ]

        ground_truth_txns = []
        running_bal = opening_balance
        total_debits = Decimal("0.00")
        total_credits = Decimal("0.00")

        # Split into Page 1 (13 transactions) and Page 2 (7 transactions)
        page1_txns = raw_txns[:13]
        page2_txns = raw_txns[13:]

        def build_txn_table(txns_subset, start_seq):
            nonlocal running_bal, total_debits, total_credits
            rows = [["Value Date", "Particulars", "Withdrawals", "Deposits", "Net Balance"]]
            curr_seq = start_seq
            for t in txns_subset:
                running_bal = running_bal + t["credit"] - t["debit"]
                total_debits += t["debit"]
                total_credits += t["credit"]

                rows.append([
                    t["date"],
                    Paragraph(t["desc"], body_style),
                    f"{t['debit']:.2f}" if t["debit"] > 0 else "-",
                    f"{t['credit']:.2f}" if t["credit"] > 0 else "-",
                    f"{running_bal:.2f}",
                ])

                ground_truth_txns.append({
                    "sequence": curr_seq,
                    "date": t["date"],
                    "description": t["desc"],
                    "debit": float(t["debit"]),
                    "credit": float(t["credit"]),
                    "balance": float(running_bal),
                })
                curr_seq += 1

            table = Table(rows, colWidths=[65, 245, 75, 75, 80])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065F46")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1FAE5")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0FDF4")]),
            ]))
            return table, curr_seq

        t1, next_seq = build_txn_table(page1_txns, 1)
        story.append(t1)

        # Force Page Break for Layout C multi-page verification
        story.append(PageBreak())

        # Page 2 Continuation
        story.append(Paragraph("OSCAR PREMIER BANK — STATEMENT CONTINUATION", title_style))
        story.append(Paragraph("Page 2 of 2 | Account: 330491028374", subtitle_style))
        story.append(Spacer(1, 8))

        t2, _ = build_txn_table(page2_txns, next_seq)
        story.append(t2)
        story.append(Spacer(1, 14))

        # Final Summary on Page 2
        summary_data = [
            [
                Paragraph("<b>Total Withdrawals:</b>", header_table_style),
                Paragraph(f"₹ {total_debits:.2f}", header_table_style),
                Paragraph("<b>Total Deposits:</b>", header_table_style),
                Paragraph(f"₹ {total_credits:.2f}", header_table_style),
                Paragraph("<b>Net Closing Balance:</b>", header_table_style),
                Paragraph(f"₹ {running_bal:.2f}", header_table_style),
            ]
        ]
        t_summary = Table(summary_data, colWidths=[90, 90, 80, 90, 90, 100])
        t_summary.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#D1FAE5")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#059669")),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("ALIGN", (3, 0), (3, 0), "RIGHT"),
            ("ALIGN", (5, 0), (5, 0), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t_summary)

        doc.build(story)

        # Save Ground Truth JSON
        ground_truth = {
            "metadata": {
                "bank_name": "OSCAR Premier Bank",
                "account_holder": "Vikramaditya Singhania",
                "account_number": "330491028374",
                "ifsc_code": "OPBL0009988",
                "branch": "Bandra Kurla Complex, Mumbai",
                "statement_period": "01/10/2026 to 25/10/2026",
                "opening_balance": float(opening_balance),
                "closing_balance": float(running_bal),
                "total_debits": float(total_debits),
                "total_credits": float(total_credits),
                "transaction_count": len(ground_truth_txns),
                "layout": "Layout C - Multi-Page Wrapped Description Table",
            },
            "transactions": ground_truth_txns,
        }

        with open(ground_truth_json_path, "w", encoding="utf-8") as f:
            json.dump(ground_truth, f, indent=2)

        return output_pdf_path, ground_truth_json_path

    @staticmethod
    def generate_scanned_pdf(output_pdf_path: str | Path, source_text_pdf_path: str | Path):
        """
        Creates a pure raster image PDF from a text PDF (flattening it to bitmap),
        simulating a scanned physical paper document with slight rotation/noise.
        """
        from PIL import Image
        import pymupdf

        output_pdf_path = Path(output_pdf_path)
        source_text_pdf_path = Path(source_text_pdf_path)

        src_doc = pymupdf.open(str(source_text_pdf_path))
        img_pages = []

        for page in src_doc:
            # Render page at 200 DPI
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            # Add slight realistic rotation / paper tilt (0.5 degrees)
            tilted_img = img.rotate(0.5, resample=Image.BICUBIC, expand=False, fillcolor="white")
            img_pages.append(tilted_img)

        src_doc.close()

        if img_pages:
            img_pages[0].save(
                str(output_pdf_path),
                save_all=True,
                append_images=img_pages[1:] if len(img_pages) > 1 else [],
                format="PDF",
                resolution=200.0,
            )

        return output_pdf_path
