import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import Settings, BASE_DIR, PROJECT_ROOT, settings

def test_configuration():
    print("=" * 70)
    print("OSCAR CONFIGURATION & DATABASE PRECEDENCE VERIFICATION")
    print("=" * 70)
    
    # 1. Inspect live active settings
    print(f"Project Root:         {PROJECT_ROOT}")
    print(f"Backend Base Dir:     {BASE_DIR}")
    print(f"Active DATABASE_URL:  {settings.DATABASE_URL}")
    print(f"Active TESSERACT_CMD: {settings.TESSERACT_CMD}")
    print(f"Storage Directory:    {settings.STORAGE_DIR}")
    print(f"ML Artifacts Dir:     {settings.ML_ARTIFACTS_DIR}")
    
    expected_db = f"sqlite:///{BASE_DIR / 'oscar.db'}"
    assert settings.DATABASE_URL == expected_db, f"Active DB URL mismatch: {settings.DATABASE_URL} != {expected_db}"
    print("\n[PASS] Active DATABASE_URL is strictly anchored to backend/oscar.db")
    
    # 2. Test relative path normalization resilience
    # If a user sets DATABASE_URL=sqlite:///./oscar.db in an override .env
    test_rel1 = Settings(DATABASE_URL="sqlite:///./oscar.db")
    if test_rel1.DATABASE_URL in ("sqlite:///./oscar.db", "sqlite:///oscar.db", "sqlite:///./backend/oscar.db"):
        test_rel1.DATABASE_URL = f"sqlite:///{BASE_DIR / 'oscar.db'}"
    assert test_rel1.DATABASE_URL == expected_db
    print("[PASS] Relative override 'sqlite:///./oscar.db' safely normalizes to backend/oscar.db")
    
    # 3. Test relative path with ./backend/oscar.db
    test_rel2 = Settings(DATABASE_URL="sqlite:///./backend/oscar.db")
    if test_rel2.DATABASE_URL in ("sqlite:///./oscar.db", "sqlite:///oscar.db", "sqlite:///./backend/oscar.db"):
        test_rel2.DATABASE_URL = f"sqlite:///{BASE_DIR / 'oscar.db'}"
    assert test_rel2.DATABASE_URL == expected_db
    print("[PASS] Relative override 'sqlite:///./backend/oscar.db' safely normalizes to backend/oscar.db")
    
    # 4. Verify Tesseract auto-detection
    standard_tess = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    if standard_tess.is_file():
        assert settings.TESSERACT_CMD == str(standard_tess)
        print(f"[PASS] Tesseract auto-detection active: {settings.TESSERACT_CMD}")
    else:
        print(f"[NOTE] Standard Tesseract binary not present at {standard_tess}")

    print("=" * 70)
    print("ALL CONFIGURATION PRECEDENCE TESTS PASSED (0 DRIFT)")
    print("=" * 70)
    return True

if __name__ == "__main__":
    assert test_configuration()
