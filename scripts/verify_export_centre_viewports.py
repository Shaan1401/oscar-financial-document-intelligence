import asyncio
import json
import urllib.request
import subprocess
import time
import shutil
import base64
from pathlib import Path
import websockets

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = ROOT / "screenshots"
DOCS_SCREENSHOTS_DIR = ROOT / "docs" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP_PROFILE = ROOT / ".chrome_temp_export"

VIEWPORTS = [
    ("1920x1080", 1920, 1080),
    ("1440x900", 1440, 900),
    ("1366x768", 1366, 768),
    ("768x1024", 768, 1024),
    ("390x844", 390, 844),
]

async def verify_export_centre():
    if TEMP_PROFILE.exists():
        shutil.rmtree(TEMP_PROFILE, ignore_errors=True)
    TEMP_PROFILE.mkdir(parents=True, exist_ok=True)

    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=9977",
        f"--user-data-dir={TEMP_PROFILE}",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900"
    ]
    proc = subprocess.Popen(cmd)

    tabs = None
    for _ in range(25):
        time.sleep(0.4)
        try:
            with urllib.request.urlopen("http://127.0.0.1:9977/json") as r:
                tabs = json.loads(r.read())
                if tabs:
                    break
        except Exception:
            pass

    if not tabs:
        print("ERROR: Failed to connect to Chrome DevTools port 9977.")
        proc.kill()
        return False

    all_passed = True

    try:
        ws_url = [t for t in tabs if t.get("type") == "page"][0]["webSocketDebuggerUrl"]
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

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")

            # First load root to initialize SPA bundles and state
            await send_cmd("Page.navigate", {"url": "http://127.0.0.1:5173/"})
            await asyncio.sleep(2.5)

            # Navigate to exports page
            await send_cmd("Page.navigate", {"url": "http://127.0.0.1:5173/exports"})
            
            # Poll until select button appears
            for _ in range(20):
                await asyncio.sleep(0.3)
                check = await send_cmd("Runtime.evaluate", {
                    "expression": "Boolean(document.querySelector('button[aria-haspopup=\"listbox\"]'))",
                    "returnByValue": True
                })
                if check.get("result", {}).get("value") is True:
                    break

            print("=" * 85)
            print("OSCAR EXPORT CENTRE — RESPONSIVE LAYOUT & OVERFLOW VERIFICATION")
            print("=" * 85)

            for name, width, height in VIEWPORTS:
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": width,
                    "height": height,
                    "deviceScaleFactor": 1,
                    "mobile": width < 800
                })
                await asyncio.sleep(0.6)

                eval_script = """
                (() => {
                    const doc = document.documentElement;
                    const body = document.body;
                    // Check horizontal overflow
                    const hasHorizontalScroll = doc.scrollWidth > doc.clientWidth + 1;
                    
                    // Statement selector button & parent card
                    const selectBtn = document.querySelector('button[aria-haspopup="listbox"]');
                    const parentCard = selectBtn ? selectBtn.closest('.rounded-xl') : null;
                    
                    let selectorFits = false;
                    let btnWidth = 0;
                    let parentWidth = 0;
                    let arrowVisible = false;
                    let textTruncated = false;
                    let buttonTitle = '';
                    
                    if (selectBtn && parentCard) {
                        const bRect = selectBtn.getBoundingClientRect();
                        const pRect = parentCard.getBoundingClientRect();
                        btnWidth = bRect.width;
                        parentWidth = pRect.width;
                        // Select button right edge must not exceed parent card right edge
                        selectorFits = bRect.right <= pRect.right + 2;
                        
                        // Check chevron down icon inside button
                        const arrow = selectBtn.querySelector('svg.lucide-chevron-down');
                        if (arrow) {
                            const aRect = arrow.getBoundingClientRect();
                            arrowVisible = (aRect.right <= bRect.right + 1) && (aRect.width > 0);
                        }
                        
                        // Check truncation & title tooltip
                        const labelSpan = selectBtn.querySelector('.truncate');
                        if (labelSpan) {
                            buttonTitle = labelSpan.getAttribute('title') || '';
                            textTruncated = labelSpan.scrollWidth > labelSpan.clientWidth;
                        }
                    }
                    
                    // Check grid columns count (desktop should be 2 cols, tablet/mobile 1 col)
                    const grid = document.querySelector('.grid.gap-6');
                    let gridCols = 1;
                    if (grid) {
                        const style = window.getComputedStyle(grid);
                        gridCols = style.gridTemplateColumns.split(' ').filter(c => c.trim().length > 0).length;
                    }

                    return {
                        viewport: `${window.innerWidth}x${window.innerHeight}`,
                        scrollWidth: doc.scrollWidth,
                        clientWidth: doc.clientWidth,
                        hasHorizontalScroll,
                        selectorFits,
                        btnWidth: Math.round(btnWidth),
                        parentWidth: Math.round(parentWidth),
                        arrowVisible,
                        textTruncated,
                        buttonTitle,
                        gridCols
                    };
                })()
                """
                res = await send_cmd("Runtime.evaluate", {"expression": eval_script, "returnByValue": True})
                val = res.get("result", {}).get("result", {}).get("value", {})

                fits = val.get("selectorFits", False)
                no_hscroll = not val.get("hasHorizontalScroll", True)
                arrow_ok = val.get("arrowVisible", False)
                grid_cols = val.get("gridCols", 1)
                expected_cols = 2 if width >= 1024 else 1

                # Criteria: selector fits within parent, no horizontal scroll, dropdown arrow visible, grid responsive
                pass_criteria = fits and no_hscroll and arrow_ok and (grid_cols == expected_cols)
                status_str = "PASS" if pass_criteria else "FAIL"
                if not pass_criteria:
                    all_passed = False

                print(f"[{status_str}] Viewport {name:10} | Selector: {val.get('btnWidth')}px / Parent: {val.get('parentWidth')}px (Fits: {fits}) | Arrow: {arrow_ok} | H-Scroll: {not no_hscroll} | Grid: {grid_cols} cols (Exp: {expected_cols})")

                # Capture screenshot
                shot = await send_cmd("Page.captureScreenshot", {"format": "png"})
                if shot.get("result", {}).get("data"):
                    img_bytes = base64.b64decode(shot["result"]["data"])
                    dest_path = SCREENSHOTS_DIR / f"export_centre_{name}.png"
                    dest_path.write_bytes(img_bytes)

                    if name == "1440x900":
                        (SCREENSHOTS_DIR / "09_export_centre.png").write_bytes(img_bytes)
                        (DOCS_SCREENSHOTS_DIR / "09_export_centre.png").write_bytes(img_bytes)

            print("=" * 85)
            return all_passed
    finally:
        proc.kill()

if __name__ == "__main__":
    success = asyncio.run(verify_export_centre())
    exit(0 if success else 1)
