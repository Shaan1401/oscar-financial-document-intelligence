import sys
import json
import sqlite3
import urllib.request
from pathlib import Path

# Set console output encoding to utf-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "backend" / "oscar.db"
BASE_URL = "http://127.0.0.1:8000/api/v1"

print("=" * 80)
print("OSCAR POST-BACKEND-RESTART PERSISTENCE VERIFICATION")
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

# 1. Health check after restart
print("\n[Step 1] Verifying Backend Health After Fresh Restart...")
health = api_get("/health")
print(f"  Backend Health: {health.get('status')} | Version: {health.get('version')}")
assert health.get("status") == "healthy", "Backend failed to start or is unhealthy!"

# 2. Get the latest statement ID (from arguments or SQLite)
conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()
cur.execute("SELECT id, filename, bank_name, status, reconciliation_status, total_debits_minor, total_credits_minor, variance_minor FROM statements ORDER BY created_at DESC LIMIT 1")
latest_stmt = cur.fetchone()
conn.close()

assert latest_stmt is not None, "No statements in database!"
target_stmt_id = latest_stmt[0]
print(f"\n[Step 2] Auditing Persisted Statement Post-Restart: {target_stmt_id}")
print(f"  Filename: {latest_stmt[1]} | Bank: {latest_stmt[2]} | Status: {latest_stmt[3]}")
print(f"  Reconciliation Status: {latest_stmt[4]} | Debits: ₹{latest_stmt[5]/100:.2f} | Credits: ₹{latest_stmt[6]/100:.2f} | Variance: ₹{latest_stmt[7]/100:.2f}")

# 3. Retrieve through API
print("\n[Step 3] Retrieving Statement via FastAPI Endpoint...")
stmt_data = api_get(f"/statements/{target_stmt_id}")
assert stmt_data["id"] == target_stmt_id, "Statement ID mismatch on API!"
assert stmt_data["statement"]["status"] == "PROCESSED", "Status should be PROCESSED"
assert stmt_data["statement"]["reconciliation_status"] == "RECONCILED", "Reconciliation status should be RECONCILED"
assert len(stmt_data["transactions"]) == 15, "All 15 transactions must persist!"

# 4. Verify that manual correction is still retained post-restart
print("\n[Step 4] Verifying Manual Human Review Correction Persistence...")
txns = stmt_data["transactions"]
# Find the corrected transaction (Txn 16 / Tax & Government)
corrected_txn = next((t for t in txns if t["category"] == "Tax & Government"), None)
print(f"  Persisted Corrected Transaction: {corrected_txn}")
assert corrected_txn is not None, "Corrected transaction was LOST after restart!"
assert corrected_txn["category"] == "Tax & Government", "Category reverted!"
assert corrected_txn["classification_method"] == "MANUAL", "Classification method reverted!"
assert corrected_txn["review_status"] == "CORRECTED", "Review status reverted!"

# 5. Verify PDF Evidence image is still accessible
print("\n[Step 5] Verifying PDF Page Preview Evidence Post-Restart...")
preview_bytes = api_get_bytes(f"/statements/{target_stmt_id}/pages/1/preview")
print(f"  Page 1 Preview: {len(preview_bytes)} bytes retrieved")
assert len(preview_bytes) > 5000, "Preview image missing after restart!"

# 6. Verify Audit Trail events persist
print("\n[Step 6] Verifying Audit Trail Persistence...")
audit_data = api_get(f"/audit?statement_id={target_stmt_id}")
event_types = [ev["event_type"] for ev in audit_data["items"]]
print(f"  Audit Events for Statement: {event_types}")
assert "UPLOAD" in event_types, "UPLOAD audit event missing!"
assert "EXTRACTION" in event_types, "EXTRACTION audit event missing!"
assert "CORRECTION" in event_types, "CORRECTION audit event missing!"
assert "RECONCILIATION" in event_types, "RECONCILIATION audit event missing!"

# 7. Check total statements and demo preservation
conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()
cur.execute("SELECT count(*) FROM statements")
total_stmts = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM transactions")
total_txns = cur.fetchone()[0]
conn.close()
print(f"\n[Step 7] Total Persisted Database State:")
print(f"  Total Statements in SQLite:   {total_stmts}")
print(f"  Total Transactions in SQLite: {total_txns}")
assert total_stmts >= 2, "Original demo statement was lost!"
assert total_txns >= 30, "Transaction data was lost!"

print("\n" + "=" * 80)
print("SUCCESS: 100% PERSISTENCE VERIFIED ACROSS REAL BACKEND RESTART!")
print("=" * 80)
