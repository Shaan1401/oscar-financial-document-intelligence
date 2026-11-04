import sys
import json
import time
import uuid
import io
import csv
import sqlite3
import urllib.request
import urllib.error
from pathlib import Path
from decimal import Decimal
import openpyxl

# Set console output encoding to utf-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))
DB_PATH = REPO_ROOT / "backend" / "oscar.db"
BASE_URL = "http://127.0.0.1:8000/api/v1"

print("=" * 80)
print("OSCAR COMPLETE END-TO-END PERSISTENCE & LIFECYCLE AUDIT")
print(f"Target Database: {DB_PATH}")
print(f"Backend URL:     {BASE_URL}")
print("=" * 80)

def api_get(endpoint: str) -> dict:
    req = urllib.request.Request(f"{BASE_URL}{endpoint}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def api_get_bytes(endpoint: str) -> bytes:
    req = urllib.request.Request(f"{BASE_URL}{endpoint}")
    with urllib.request.urlopen(req) as resp:
        return resp.read()

def api_post(endpoint: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def upload_pdf(filename: str, pdf_bytes: bytes) -> dict:
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    body = io.BytesIO()
    body.write(f"--{boundary}\r\n".encode("utf-8"))
    body.write(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.write(b"Content-Type: application/pdf\r\n\r\n")
    body.write(pdf_bytes)
    body.write(b"\r\n")
    body.write(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        f"{BASE_URL}/statements/upload?auto_process=true",
        data=body.getvalue(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

# Step 1: Health check
print("\n[Step 1] Checking Backend Health...")
health = api_get("/health")
print(f"  Backend Health: {health.get('status')} | Version: {health.get('version')} | Full Name: {health.get('full_name')}")
assert health.get("status") == "healthy", "Backend is not healthy!"

# Step 2: Generate a fresh synthetic PDF with unique identifier
print("\n[Step 2] Generating Fresh Unique Synthetic PDF...")
from app.extraction.synthetic_generator import SyntheticStatementGenerator

unique_suffix = int(time.time())
test_pdf_path = REPO_ROOT / "sample_data" / "pdf" / f"e2e_audit_{unique_suffix}.pdf"
test_gt_path = REPO_ROOT / "sample_data" / "ground_truth" / f"e2e_audit_{unique_suffix}_truth.json"

SyntheticStatementGenerator.generate_layout_a(test_pdf_path, test_gt_path)
pdf_bytes = test_pdf_path.read_bytes()
print(f"  Generated test PDF: {test_pdf_path.name} ({len(pdf_bytes)} bytes)")

# Step 3: Upload via API
print("\n[Step 3] Uploading Synthetic Statement via API...")
upload_res = upload_pdf(test_pdf_path.name, pdf_bytes)
new_statement_id = upload_res["id"]
print(f"  Upload Success! Assigned Statement ID: {new_statement_id}")
print(f"  Status: {upload_res.get('status')} | Recon: {upload_res.get('reconciliation_status')} | Txn Count: {upload_res.get('transaction_count')}")
assert upload_res.get("status") == "PROCESSED", "Statement status should be PROCESSED"
assert upload_res.get("transaction_count") > 0, "Transactions were not extracted"

# Step 4: Verify Database Persistence Immediately
print("\n[Step 4] Querying SQLite Directly for New Statement & Transactions...")
conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

cur.execute("SELECT id, filename, bank_name, status, reconciliation_status, opening_balance_minor, closing_balance_minor FROM statements WHERE id=?", (new_statement_id,))
stmt_row = cur.fetchone()
print(f"  SQLite Statement Row: {stmt_row}")
assert stmt_row is not None, "Statement row not found in SQLite!"

cur.execute("SELECT count(*) FROM transactions WHERE statement_id=?", (new_statement_id,))
txn_count_db = cur.fetchone()[0]
print(f"  SQLite Transactions for Statement: {txn_count_db} rows")
assert txn_count_db == upload_res["transaction_count"], "DB transaction count mismatch!"

cur.execute("SELECT holder_name, masked_number, ifsc_code FROM accounts WHERE statement_id=?", (new_statement_id,))
acc_row = cur.fetchone()
print(f"  SQLite Account Row: {acc_row}")
assert acc_row is not None, "Account row not found in SQLite!"

# Inspect first 3 transactions
cur.execute("SELECT id, date, description, debit_minor, credit_minor, balance_minor, category, classification_method, confidence_score FROM transactions WHERE statement_id=? ORDER BY id ASC LIMIT 3", (new_statement_id,))
sample_txns = cur.fetchall()
print("  Sample Transactions in SQLite:")
for stxn in sample_txns:
    print(f"    Txn ID {stxn[0]}: {stxn[1]} | {stxn[2][:25]}... | Dr: ₹{stxn[3]/100:.2f} | Cr: ₹{stxn[4]/100:.2f} | Bal: ₹{stxn[5]/100:.2f} | Cat: {stxn[6]} ({stxn[7]}, Conf: {stxn[8]})")

target_txn_id = sample_txns[0][0]
orig_cat = sample_txns[0][6]
conn.close()

# Step 5: Test PDF Evidence Viewer Endpoint
print("\n[Step 5] Testing Page Preview Evidence API...")
preview_bytes = api_get_bytes(f"/statements/{new_statement_id}/pages/1/preview")
print(f"  Rendered Page 1 Preview Image: {len(preview_bytes)} bytes (PNG format)")
assert len(preview_bytes) > 5000, "Preview image too small or empty!"

# Step 6: Perform Human Review Correction
print(f"\n[Step 6] Performing Human Review Correction on Transaction {target_txn_id}...")
print(f"  Original Category: {orig_cat}")
correct_res = api_post(f"/reviews/{target_txn_id}/correct", {
    "new_category": "Tax & Government",
    "reason": "E2E Automated Persistence Audit Test"
})
print(f"  Correction Response: {correct_res}")
assert correct_res["review_status"] == "CORRECTED"
assert correct_res["category"] == "Tax & Government"

# Check SQLite for updated transaction and audit event
conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()
cur.execute("SELECT category, classification_method, review_status FROM transactions WHERE id=?", (target_txn_id,))
updated_txn = cur.fetchone()
print(f"  Updated SQLite Txn: Category={updated_txn[0]}, Method={updated_txn[1]}, ReviewStatus={updated_txn[2]}")
assert updated_txn[0] == "Tax & Government"
assert updated_txn[1] == "MANUAL"
assert updated_txn[2] == "CORRECTED"

cur.execute("SELECT event_type, actor, details FROM audit_events WHERE statement_id=? AND transaction_id=? ORDER BY id DESC LIMIT 1", (new_statement_id, target_txn_id))
audit_row = cur.fetchone()
print(f"  Recorded Audit Event: {audit_row}")
assert audit_row[0] == "CORRECTION"
conn.close()

# Step 7: Run Reconciliation
print(f"\n[Step 7] Running Mathematical Reconciliation on Statement {new_statement_id}...")
recon_res = api_post(f"/reconciliation/{new_statement_id}/run", {})
print(f"  Reconciliation Result: Status={recon_res['status']} | Expected Closing=₹{recon_res['expected_closing_balance']:.2f} | Actual Closing=₹{recon_res['actual_closing_balance']:.2f} | Variance=₹{recon_res['variance']:.2f}")
print(f"  Recalculated At: {recon_res.get('recalculated_at')}")

# Step 8: Test Exports (Excel and CSV)
print("\n[Step 8] Testing Excel and CSV Exports...")
excel_data = api_get_bytes(f"/exports/{new_statement_id}/excel")
print(f"  Downloaded Excel workbook: {len(excel_data)} bytes")
wb = openpyxl.load_workbook(io.BytesIO(excel_data))
sheet_names = wb.sheetnames
print(f"  Excel Sheets: {sheet_names}")
assert "Transactions" in sheet_names
assert "Reconciliation" in sheet_names
assert "Account Summary" in sheet_names

# Check that corrected category is present in Excel
ws_txns = wb["Transactions"]
excel_rows = list(ws_txns.iter_rows(values_only=True))
print(f"  Excel Data Rows: {len(excel_rows) - 1} transactions")
assert len(excel_rows) - 1 == txn_count_db

# Find corrected transaction row
found_corrected = False
for r in excel_rows[1:]:
    if r[6] == "Tax & Government" and r[7] == "MANUAL":
        found_corrected = True
        print(f"  Found corrected transaction in Excel: Date={r[0]} | Cat={r[6]} | Method={r[7]}")
        break
assert found_corrected, "Corrected category not reflected in Excel export!"

csv_data = api_get_bytes(f"/exports/{new_statement_id}/csv").decode("utf-8")
print(f"  Downloaded CSV export: {len(csv_data)} characters")
csv_reader = list(csv.reader(io.StringIO(csv_data)))
print(f"  CSV Data Rows: {len(csv_reader) - 1} transactions")
assert len(csv_reader) - 1 == txn_count_db

# Step 9: Pre-Restart Snapshot
print("\n[Step 9] Taking Pre-Restart Snapshot of Statement Data...")
pre_statement = api_get(f"/statements/{new_statement_id}")
print(f"  Pre-restart: ID={pre_statement['id']} | Txns={len(pre_statement['transactions'])} | Recon={pre_statement['statement']['reconciliation_status']}")

# Summary of Phase 1
print("\n" + "=" * 80)
print("PHASE 1 COMPLETE: Statement successfully created, processed, reviewed, reconciled, and exported.")
print(f"Statement ID to verify across restart: {new_statement_id}")
print("=" * 80)
