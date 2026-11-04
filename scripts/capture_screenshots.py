import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

PAGES = [
    ("01_dashboard.png", "http://127.0.0.1:5173/"),
    ("02_evidence_viewer.png", "http://127.0.0.1:5173/statements/f5c41bef-3e8a-456e-ac1a-0fe2b5c7c111"),
    ("03_reconciliation.png", "http://127.0.0.1:5173/reconciliation"),
    ("04_reviews.png", "http://127.0.0.1:5173/reviews"),
    ("05_classification_insights.png", "http://127.0.0.1:5173/classification"),
    ("06_analytics.png", "http://127.0.0.1:5173/analytics"),
    ("07_transaction_explorer.png", "http://127.0.0.1:5173/transactions"),
    ("08_statement_history.png", "http://127.0.0.1:5173/statements"),
    ("09_export_centre.png", "http://127.0.0.1:5173/export"),
    ("10_audit_trail.png", "http://127.0.0.1:5173/audit"),
    ("11_settings.png", "http://127.0.0.1:5173/settings"),
    ("12_dashboard_dark.png", "http://127.0.0.1:5173/"),
    ("13_analytics_dark.png", "http://127.0.0.1:5173/analytics"),
    ("14_upload.png", "http://127.0.0.1:5173/upload"),
]

def capture_all():
    print(f"Starting screenshot capture to {SCREENSHOTS_DIR}...")
    for filename, url in PAGES:
        out_path = SCREENSHOTS_DIR / filename
        cmd = [
            CHROME_PATH,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--window-size=1440,900",
            "--virtual-time-budget=3000",
        ]
        if "_dark" in filename:
            cmd.append("--force-dark-mode")
            cmd.append("--blink-settings=forceDarkModeEnabled=true")

        cmd.extend([f"--screenshot={out_path}", url])
        print(f"Capturing {filename} from {url}...")
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=25)
            if out_path.exists():
                size_kb = out_path.stat().st_size / 1024
                print(f"  OK: {filename} ({size_kb:.1f} KB)")
            else:
                print(f"  Warning: File not created for {filename}")
        except Exception as e:
            print(f"  Error capturing {filename}: {e}")

    # Remove temporary test file if present
    test_file = SCREENSHOTS_DIR / "test.png"
    if test_file.exists():
        test_file.unlink()

    print("Screenshot capture complete!")

if __name__ == "__main__":
    capture_all()
