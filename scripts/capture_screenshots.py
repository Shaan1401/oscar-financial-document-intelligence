import asyncio
import json
import base64
import urllib.request
import subprocess
import time
import sqlite3
import shutil
from pathlib import Path
from PIL import Image
import websockets

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = ROOT / "screenshots"
DOCS_SCREENSHOTS_DIR = ROOT / "docs" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_PROFILE = ROOT / ".chrome_temp"

def get_first_statement_id() -> str:
    db_path = ROOT / "backend" / "oscar.db"
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM statements LIMIT 1")
        row = cur.fetchone()
        conn.close()
        if row:
            return str(row[0])
    return "eb500682-41d8-460d-b2e2-3d5f3d18d02d"

PAGES = [
    ("01_dashboard.png", "/", False),
    ("02_evidence_viewer.png", "/statements/{stmt_id}", False),
    ("03_reconciliation.png", "/reconciliation", False),
    ("04_reviews.png", "/reviews", False),
    ("05_classification_insights.png", "/classification", False),
    ("06_analytics.png", "/analytics", False),
    ("07_transaction_explorer.png", "/transactions", False),
    ("08_statement_history.png", "/statements", False),
    ("09_export_centre.png", "/exports", False),
    ("10_audit_trail.png", "/audit", False),
    ("11_settings.png", "/settings", False),
    ("12_dashboard_dark.png", "/", True),
    ("13_analytics_dark.png", "/analytics", True),
    ("14_upload.png", "/upload", False),
]

async def capture_all_cdp():
    stmt_id = get_first_statement_id()
    print(f"Using statement ID: {stmt_id} for Evidence Viewer")

    if TEMP_PROFILE.exists():
        shutil.rmtree(TEMP_PROFILE, ignore_errors=True)
    TEMP_PROFILE.mkdir(parents=True, exist_ok=True)

    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=9988",
        f"--user-data-dir={TEMP_PROFILE}",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1440,900"
    ]
    proc = subprocess.Popen(cmd)

    tabs = None
    for _ in range(15):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen("http://127.0.0.1:9988/json") as r:
                tabs = json.loads(r.read())
                if tabs:
                    break
        except Exception:
            pass

    if not tabs:
        print("Failed to connect to Chrome DevTools port.")
        proc.kill()
        return

    try:
        ws_url = [t for t in tabs if t.get("type") == "page"][0]["webSocketDebuggerUrl"]
        print(f"Connected to Chrome CDP: {ws_url}")

        async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
            msg_id = 1

            async def send_cmd(method: str, params: dict = None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                payload = {"id": cid, "method": method}
                if params:
                    payload["params"] = params
                await ws.send(json.dumps(payload))
                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    if data.get("id") == cid:
                        return data

            # Enable Page and Runtime
            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")

            # 1. Initial Page Load to initialize Vite and React
            print("Performing initial page load to http://127.0.0.1:5173/...")
            await send_cmd("Page.navigate", {"url": "http://127.0.0.1:5173/"})
            await asyncio.sleep(3.5)

            # 2. Iterate through all pages via SPA client-side routing
            for filename, route_template, is_dark in PAGES:
                route = route_template.replace("{stmt_id}", stmt_id)
                print(f"Capturing {filename} via route {route} (Dark: {is_dark})...")

                # Navigate in SPA without reloading page context
                nav_script = f"window.history.pushState(null, '', '{route}'); window.dispatchEvent(new PopStateEvent('popstate'));"
                await send_cmd("Runtime.evaluate", {"expression": nav_script})

                # Allow React components, API fetches, and charts to render
                await asyncio.sleep(2.5)

                # Set dark/light theme
                theme_script = (
                    "document.documentElement.classList.add('dark');"
                    if is_dark
                    else "document.documentElement.classList.remove('dark');"
                )
                await send_cmd("Runtime.evaluate", {"expression": theme_script})
                await asyncio.sleep(0.5)

                # Capture screenshot
                shot_resp = await send_cmd("Page.captureScreenshot", {"format": "png"})
                b64_data = shot_resp.get("result", {}).get("data")
                if b64_data:
                    img_bytes = base64.b64decode(b64_data)
                    out_path = SCREENSHOTS_DIR / filename
                    out_path.write_bytes(img_bytes)

                    # Mirror to docs/screenshots
                    docs_path = DOCS_SCREENSHOTS_DIR / filename
                    docs_path.write_bytes(img_bytes)

                    size_kb = len(img_bytes) / 1024
                    print(f"  SUCCESS: {filename} ({size_kb:.1f} KB)")
                else:
                    print(f"  WARNING: Failed to capture {filename}")

    finally:
        proc.kill()
        proc.wait()
        shutil.rmtree(TEMP_PROFILE, ignore_errors=True)

        # Cleanup temporary files
        for temp_name in ["01_dash.png", "03_recon.png", "04_rev.png", "06_anal.png", "07_tx.png", "test_dash.png", "test_txns.png", "test.png"]:
            tp = SCREENSHOTS_DIR / temp_name
            if tp.exists():
                tp.unlink()

        print("Chrome CDP capture completed and cleaned up.")

if __name__ == "__main__":
    asyncio.run(capture_all_cdp())
