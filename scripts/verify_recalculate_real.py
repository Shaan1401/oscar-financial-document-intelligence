import sys
import json
import urllib.request
from pathlib import Path

# Force UTF-8 stdout
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.database.session import SessionLocal
from app.database.models import Statement

def run_test():
    db = SessionLocal()
    first_stmt = db.query(Statement).first()
    if not first_stmt:
        print("ERROR: No statements in database!")
        db.close()
        return
    stmt_id = first_stmt.id
    db.close()
    api_url = f"http://127.0.0.1:8000/api/v1/reconciliation/{stmt_id}/run"

    print(f"=== OSCAR RECALCULATION BEHAVIOR VERIFICATION (Statement ID: {stmt_id}) ===")

    # TEST 1: Reconciled state
    req1 = urllib.request.Request(api_url, data=b"", method="POST")
    with urllib.request.urlopen(req1) as resp:
        res1 = json.loads(resp.read().decode())
    print("\n--- Test 1: Reconciled Statement ---")
    print(f"Statement: {res1['statement_id']}")
    print(f"Status: {res1['status']}")
    print(f"Expected Closing: ₹{res1['expected_closing_balance']:,.2f}")
    print(f"Actual Closing: ₹{res1['actual_closing_balance']:,.2f}")
    print(f"Variance: ₹{res1['variance']:,.2f}")
    print(f"Is Reconciled: {res1['is_reconciled']}")
    print(f"Recalculated At: {res1.get('recalculated_at')}")
    assert res1['status'] == "RECONCILED", f"Expected RECONCILED, got {res1['status']}"
    assert res1['variance'] == 0.0, f"Expected 0.0 variance, got {res1['variance']}"
    assert res1['is_reconciled'] is True

    # TEST 2: Deliberately introduce mismatch of +₹1,500.00
    print("\n--- Test 2: Deliberately Introduced Mismatch (+₹1,500.00) ---")
    db = SessionLocal()
    try:
        stmt = db.query(Statement).filter(Statement.id == stmt_id).first()
        orig_closing_minor = stmt.closing_balance_minor
        stmt.closing_balance_minor = orig_closing_minor + 150000  # +1,500.00 INR
        db.commit()
    finally:
        db.close()

    req2 = urllib.request.Request(api_url, data=b"", method="POST")
    with urllib.request.urlopen(req2) as resp:
        res2 = json.loads(resp.read().decode())
    print(f"Status: {res2['status']}")
    print(f"Expected Closing: ₹{res2['expected_closing_balance']:,.2f}")
    print(f"Actual Closing: ₹{res2['actual_closing_balance']:,.2f}")
    print(f"Variance: ₹{res2['variance']:,.2f}")
    print(f"Is Reconciled: {res2['is_reconciled']}")
    print(f"Exceptions: {res2['exceptions']}")
    assert res2['status'] == "MISMATCH", f"Expected MISMATCH, got {res2['status']}"
    assert res2['variance'] == 1500.0, f"Expected 1500.0 variance, got {res2['variance']}"
    assert res2['is_reconciled'] is False

    # TEST 3: Restore to exact balance
    print("\n--- Test 3: Restored Reconciled Calculation ---")
    db = SessionLocal()
    try:
        stmt = db.query(Statement).filter(Statement.id == stmt_id).first()
        stmt.closing_balance_minor = orig_closing_minor
        db.commit()
    finally:
        db.close()

    req3 = urllib.request.Request(api_url, data=b"", method="POST")
    with urllib.request.urlopen(req3) as resp:
        res3 = json.loads(resp.read().decode())
    print(f"Status: {res3['status']}")
    print(f"Expected Closing: ₹{res3['expected_closing_balance']:,.2f}")
    print(f"Actual Closing: ₹{res3['actual_closing_balance']:,.2f}")
    print(f"Variance: ₹{res3['variance']:,.2f}")
    print(f"Is Reconciled: {res3['is_reconciled']}")
    assert res3['status'] == "RECONCILED", f"Expected RECONCILED, got {res3['status']}"
    assert res3['variance'] == 0.0, f"Expected 0.0 variance, got {res3['variance']}"
    assert res3['is_reconciled'] is True

    print("\n>>> ALL 3 RECALCULATION TESTS PASSED WITH REAL DB & FASTAPI BACKEND! <<<")

if __name__ == "__main__":
    run_test()
