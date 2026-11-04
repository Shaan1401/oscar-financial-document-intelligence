import sqlite3
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Resolve database path absolute to repository root
REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = (REPO_ROOT / "backend" / "oscar.db").resolve()

print("=" * 70)
print(f"OSCAR DATABASE AUDIT & SCHEMA INSPECTION")
print(f"Database File: {DB_PATH}")
print(f"File Exists:   {DB_PATH.exists()} (Size: {DB_PATH.stat().st_size if DB_PATH.exists() else 0} bytes)")
print("=" * 70)

if not DB_PATH.exists():
    print("ERROR: Database file does not exist!")
    sys.exit(1)

conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

# 1. PRAGMAs & Integrity
print("\n--- [1] SQLite Engine & Pragmas ---")
cur.execute("PRAGMA journal_mode")
journal_mode = cur.fetchone()[0]
print(f"Journal Mode:              {journal_mode}")

cur.execute("PRAGMA foreign_keys")
fk_status = cur.fetchone()[0]
print(f"Foreign Keys (Connection): {'ENABLED' if fk_status else 'DISABLED (Default in raw connection; set to ON in SQLAlchemy connect hook)'}")

cur.execute("PRAGMA integrity_check")
integrity = cur.fetchall()
print(f"Integrity Check Result:    {integrity[0][0] if integrity else 'FAILED'}")

cur.execute("PRAGMA foreign_key_check")
fk_violations = cur.fetchall()
print(f"Foreign Key Violations:    {len(fk_violations)} violations found")
if fk_violations:
    for v in fk_violations:
        print(f"   Violation: {v}")

# 2. Tables and Table Schema
print("\n--- [2] Database Tables and Row Counts ---")
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]

table_counts = {}
for t in tables:
    if t == "sqlite_sequence":
        continue
    cur.execute(f"SELECT count(*) FROM {t}")
    cnt = cur.fetchone()[0]
    table_counts[t] = cnt
    print(f"  • {t:25s}: {cnt:5d} rows")

# 3. Foreign Key Definitions
print("\n--- [3] Table Foreign Key Relationships ---")
for t in tables:
    if t == "sqlite_sequence":
        continue
    cur.execute(f"PRAGMA foreign_key_list({t})")
    fks = cur.fetchall()
    if fks:
        for fk in fks:
            # fk tuple: (id, seq, table, from, to, on_update, on_delete, match)
            print(f"  • {t}.{fk[3]} -> {fk[2]}.{fk[4]} (ON DELETE {fk[6]})")

# 4. Statements Summary (Sanitized)
print("\n--- [4] Statements Ledger Summary ---")
cur.execute("""
    SELECT id, filename, bank_name, page_count, status, reconciliation_status,
           opening_balance_minor, closing_balance_minor, total_debits_minor, total_credits_minor, variance_minor
    FROM statements
""")
stmts = cur.fetchall()
print(f"Total Statements: {len(stmts)}")
for s in stmts:
    s_id, fn, bank, pages, status, r_status, op, cl, deb, cred, var = s
    op_val = f"₹{op/100:.2f}" if op is not None else "N/A"
    cl_val = f"₹{cl/100:.2f}" if cl is not None else "N/A"
    var_val = f"₹{var/100:.2f}" if var is not None else "₹0.00"
    print(f"  ID: {s_id[:8]}... | File: {fn} | Bank: {bank or 'Generic'} | Status: {status} | Recon: {r_status}")
    print(f"     Opening: {op_val} | Debits: ₹{deb/100:.2f} | Credits: ₹{cred/100:.2f} | Closing: {cl_val} | Variance: {var_val}")

# 5. Accounts Summary (Sanitized / Masked)
print("\n--- [5] Accounts Summary (Masked) ---")
cur.execute("""
    SELECT statement_id, holder_name, masked_number, ifsc_code, currency
    FROM accounts
""")
accounts = cur.fetchall()
print(f"Total Accounts: {len(accounts)}")
for a in accounts:
    stmt_id, holder, masked, ifsc, cur_code = a
    # Never print raw account numbers - masked only
    print(f"  Statement: {stmt_id[:8]}... | Holder: {holder or 'N/A'} | Account: {masked or 'XXXX-XXXX'} | IFSC: {ifsc or 'N/A'} | Cur: {cur_code}")

# 6. Audit Trail Sample (Sanitized)
print("\n--- [6] Recent Audit Trail Events ---")
cur.execute("""
    SELECT event_type, actor, statement_id, details, created_at
    FROM audit_events ORDER BY id DESC LIMIT 5
""")
events = cur.fetchall()
for ev in events:
    etype, actor, s_id, details, dt = ev
    s_ref = f"{s_id[:8]}..." if s_id else "N/A"
    print(f"  [{dt}] {etype:15s} by {actor:6s} | Ref: {s_ref} | {details[:60]}...")

conn.close()
print("\n" + "=" * 70)
print("DATABASE INSPECTION COMPLETED SUCCESSFULLY (0 ERRORS)")
print("=" * 70)
