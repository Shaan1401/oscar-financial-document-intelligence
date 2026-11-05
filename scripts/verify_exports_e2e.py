import urllib.request
import json
import io
import csv
import openpyxl
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def test_exports_e2e():
    print("=" * 70)
    print("PART 5 — EXCEL & CSV EXPORT E2E VERIFICATION")
    print("=" * 70)

    # 1. Fetch statements from live API
    url = "http://127.0.0.1:8000/api/v1/statements"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200, f"Failed to fetch statements: {resp.status}"
        data = json.loads(resp.read().decode())
        statements = data.get("value", data) if isinstance(data, dict) else data

    assert len(statements) > 0, "No statements found in database"
    stmt = statements[0]
    stmt_id = stmt["id"]
    filename = stmt["filename"]
    print(f"[OK] Found statement: {stmt_id} ('{filename}')")

    # 2. Download Excel export
    excel_url = f"http://127.0.0.1:8000/api/v1/exports/{stmt_id}/excel"
    with urllib.request.urlopen(excel_url) as resp:
        assert resp.status == 200, f"Excel download failed: {resp.status}"
        assert resp.headers.get_content_type() in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/octet-stream"]
        excel_bytes = resp.read()
    print(f"[OK] Downloaded Excel workbook: {len(excel_bytes)} bytes")

    # 3. Inspect Excel workbook programmatically with openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    sheet_names = wb.sheetnames
    print(f"[OK] Excel Worksheets ({len(sheet_names)}): {sheet_names}")
    expected_sheets = ["Transactions", "Account Summary", "Reconciliation", "Audit Info"]
    for s in expected_sheets:
        assert s in sheet_names, f"Missing expected sheet: {s}"

    # Verify Transactions Sheet
    ws_txn = wb["Transactions"]
    header_row = [cell.value for cell in ws_txn[1]]
    print(f"[OK] Transactions Headers ({len(header_row)}): {header_row[:6]}...")
    assert "Date" in header_row
    assert "Description" in header_row
    assert "Debit" in header_row
    assert "Credit" in header_row
    assert "Balance" in header_row
    assert "Category" in header_row

    excel_txns_count = ws_txn.max_row - 1
    print(f"[OK] Excel Transactions Row Count: {excel_txns_count}")

    # Verify Reconciliation Sheet
    ws_rec = wb["Reconciliation"]
    rec_rows = {row[0]: row[1] for row in ws_rec.iter_rows(values_only=True) if row and len(row) >= 2 and row[0]}
    print(f"[OK] Reconciliation Sheet Data: {rec_rows}")
    assert "Reconciliation Status" in rec_rows
    assert rec_rows["Reconciliation Status"] == "RECONCILED"
    assert rec_rows.get("Variance") == 0.0

    # 4. Download CSV export
    csv_url = f"http://127.0.0.1:8000/api/v1/exports/{stmt_id}/csv"
    with urllib.request.urlopen(csv_url) as resp:
        assert resp.status == 200, f"CSV download failed: {resp.status}"
        csv_text = resp.read().decode("utf-8")
    print(f"[OK] Downloaded CSV text: {len(csv_text)} characters")

    # Parse CSV
    reader = list(csv.reader(io.StringIO(csv_text)))
    assert len(reader) >= 2, "CSV has no data rows"
    csv_headers = reader[0]
    csv_rows = reader[1:]
    print(f"[OK] CSV Headers ({len(csv_headers)}): {csv_headers[:6]}...")
    print(f"[OK] CSV Data Rows: {len(csv_rows)}")
    assert len(csv_rows) == excel_txns_count, f"Row count mismatch: CSV {len(csv_rows)} vs Excel {excel_txns_count}"

    # 5. Verify against direct SQLite records
    conn = sqlite3.connect(ROOT / "backend" / "oscar.db")
    c = conn.cursor()
    c.execute("SELECT count(*) FROM transactions WHERE statement_id = ?", (stmt_id,))
    db_count = c.fetchone()[0]
    conn.close()
    print(f"[OK] Database Transaction Count: {db_count}")
    assert len(csv_rows) == db_count, f"Export count {len(csv_rows)} != DB count {db_count}"

    # 6. Test CSV Formula-Injection Protection & Negative Amounts
    from app.exports.csv_exporter import CSVExporter
    
    # Injection test cases
    assert CSVExporter.sanitize_field("=cmd|'/C calc'!A0") == "'=cmd|'/C calc'!A0"
    assert CSVExporter.sanitize_field("+12345") == "'+12345"
    assert CSVExporter.sanitize_field("@SUM(1,2)") == "'@SUM(1,2)"
    assert CSVExporter.sanitize_field("-cmd|'/C calc'!A0") == "'-cmd|'/C calc'!A0"
    assert CSVExporter.sanitize_field("Normal Description") == "Normal Description"
    print("[OK] Formula injection sanitization verified: prepends single quote to dangerous prefixes (=, +, -, @, \\t, \\r)")

    # Numeric formatting test (negative balances remain valid numbers)
    from app.database.models import Transaction
    dummy_txn = Transaction(
        id="dummy",
        statement_id="dummy",
        date="2026-10-15",
        description="Overdraft Fee",
        debit_minor=5000,
        credit_minor=0,
        balance_minor=-25000,
        currency="INR",
        exponent=2,
        category="Bank Charges",
        classification_method="rule",
        confidence_score=0.99,
        review_status="APPROVED",
        source_page=1,
        row_sequence=1
    )
    dummy_csv = CSVExporter.export_transactions([dummy_txn])
    parsed_dummy = list(csv.reader(io.StringIO(dummy_csv)))
    data_row = parsed_dummy[1]
    debit_col = data_row[2]
    credit_col = data_row[3]
    balance_col = data_row[4]
    
    print(f"[OK] Dummy row amounts: Debit={debit_col}, Credit={credit_col}, Balance={balance_col}")
    assert debit_col == "50.00"
    assert credit_col == "0.00"
    assert balance_col == "-250.00", f"Negative balance corrupted: {balance_col}"
    # Verify it can be converted to float cleanly without parsing error
    assert float(balance_col) == -250.0
    print("[OK] Negative amount verified: numerically exact '-250.00', uncorrupted by text sanitizers")

    print("=" * 70)
    print("PART 5 EXPORT VERIFICATION PASSED COMPLETELY (0 ERRORS)")
    print("=" * 70)
    return True

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT / "backend"))
    assert test_exports_e2e()
