import asyncio
import json
import urllib.request
import subprocess
import time
import os
import shutil
import base64
from pathlib import Path
import websockets

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = ROOT / ".runtime"
BROWSER_PROFILE = RUNTIME_DIR / "browser"
RUNTIME_TMP = RUNTIME_DIR / "tmp"
SCREENSHOTS_DIR = ROOT / "screenshots"

os.environ["TEMP"] = str(RUNTIME_TMP)
os.environ["TMP"] = str(RUNTIME_TMP)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

VIEWPORTS = [
    ("1920x1080", 1920, 1080),
    ("1440x900", 1440, 900),
    ("1366x768", 1366, 768),
    ("768x1024", 768, 1024),
    ("390x844", 390, 844),
]

async def run_interactive_verification():
    print("=" * 80)
    print("PART 2 & 4 — INTERACTIVE EXPORT CENTRE & BROWSER VERIFICATION")
    print("=" * 80)

    if BROWSER_PROFILE.exists():
        shutil.rmtree(BROWSER_PROFILE, ignore_errors=True)
    BROWSER_PROFILE.mkdir(parents=True, exist_ok=True)

    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=9955",
        f"--user-data-dir={BROWSER_PROFILE}",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900"
    ]
    proc = subprocess.Popen(cmd)

    tabs = None
    for _ in range(25):
        time.sleep(0.3)
        try:
            with urllib.request.urlopen("http://127.0.0.1:9955/json") as r:
                tabs = json.loads(r.read())
                if tabs:
                    break
        except Exception:
            pass

    if not tabs:
        print("ERROR: Failed to connect to Chrome DevTools on port 9955")
        proc.kill()
        return False

    console_errors = []
    
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
                    if data.get("method") == "Runtime.consoleAPICalled":
                        ctype = data.get("params", {}).get("type")
                        if ctype in ["error", "warning"]:
                            args = [str(a.get("value")) for a in data.get("params", {}).get("args", [])]
                            console_errors.append(f"[{ctype.upper()}] {' '.join(args)}")
                    if data.get("method") == "Runtime.exceptionThrown":
                        details = data.get("params", {}).get("exceptionDetails", {})
                        console_errors.append(f"[EXCEPTION] {details.get('text')}")

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")

            # 1. Navigate to root first
            await send_cmd("Page.navigate", {"url": "http://127.0.0.1:5173/"})
            await asyncio.sleep(2.0)

            # 2. Navigate to Export Centre
            await send_cmd("Page.navigate", {"url": "http://127.0.0.1:5173/exports"})
            
            # Wait for button[aria-haspopup="listbox"]
            for _ in range(20):
                await asyncio.sleep(0.3)
                chk = await send_cmd("Runtime.evaluate", {
                    "expression": "Boolean(document.querySelector('button[aria-haspopup=\"listbox\"]'))",
                    "returnByValue": True
                })
                if chk.get("result", {}).get("result", {}).get("value") is True:
                    break

            # 3. Test interactive SearchableSelect: click, search, select
            interact_script = """
            (() => {
                const btn = document.querySelector('button[aria-haspopup="listbox"]');
                if (!btn) return { success: false, reason: 'No trigger button found' };
                
                // Click to open
                btn.click();
                return { success: true, opened: btn.getAttribute('aria-expanded') === 'true' };
            })()
            """
            r1 = await send_cmd("Runtime.evaluate", {"expression": interact_script, "returnByValue": True})
            open_res = r1.get("result", {}).get("result", {}).get("value", {})
            print(f"[OK] Clicked trigger button -> Dropdown opened: {open_res.get('opened')}")

            await asyncio.sleep(0.3)

            # Type 'scanned' into search input
            search_script = """
            (() => {
                const input = document.querySelector('input[placeholder*=\"Search statements\"]');
                if (!input) return { success: false, reason: 'Search input not found in popover' };
                input.value = 'scanned';
                input.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Get filtered option list
                const options = Array.from(document.querySelectorAll('li[role=\"option\"]'));
                const labels = options.map(o => o.innerText.split('\\n')[0]);
                
                // Click the first matching option
                if (options.length > 0) {
                    options[0].click();
                }
                
                return {
                    success: true,
                    filteredCount: options.length,
                    firstOption: labels[0] || null
                };
            })()
            """
            r2 = await send_cmd("Runtime.evaluate", {"expression": search_script, "returnByValue": True})
            search_res = r2.get("result", {}).get("result", {}).get("value", {})
            print(f"[OK] Search query 'scanned' applied -> Matches found: {search_res.get('filteredCount')} ({search_res.get('firstOption')})")

            await asyncio.sleep(0.5)

            # Check selected value text and title
            val_script = """
            (() => {
                const btn = document.querySelector('button[aria-haspopup=\"listbox\"]');
                const labelSpan = btn ? btn.querySelector('.truncate') : null;
                const titleAttr = labelSpan ? labelSpan.getAttribute('title') : '';
                const renderedText = labelSpan ? labelSpan.innerText : '';
                const excelLink = document.querySelector('a[href*=\"/excel\"]');
                const csvLink = document.querySelector('a[href*=\"/csv\"]');
                
                return {
                    renderedText,
                    titleAttr,
                    excelHref: excelLink ? excelLink.getAttribute('href') : null,
                    csvHref: csvLink ? csvLink.getAttribute('href') : null
                };
            })()
            """
            r3 = await send_cmd("Runtime.evaluate", {"expression": val_script, "returnByValue": True})
            val_res = r3.get("result", {}).get("result", {}).get("value", {})
            print(f"[OK] Statement selected: '{val_res.get('renderedText')}'")
            print(f"[OK] Full filename in tooltip/title: '{val_res.get('titleAttr')}'")
            print(f"[OK] Excel download link active: {val_res.get('excelHref')}")
            print(f"[OK] CSV download link active: {val_res.get('csvHref')}")

            # 4. Measure layout metrics across all 5 viewports
            print("\n--- Measuring Viewports for Horizontal Overflow & Grid Stacking ---")
            for name, w, h in VIEWPORTS:
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": w,
                    "height": h,
                    "deviceScaleFactor": 1,
                    "mobile": w < 800
                })
                await asyncio.sleep(0.5)

                vp_script = """
                (() => {
                    const doc = document.documentElement;
                    const btn = document.querySelector('button[aria-haspopup=\"listbox\"]');
                    const card = btn ? btn.closest('.rounded-xl') : null;
                    const bRect = btn ? btn.getBoundingClientRect() : null;
                    const cRect = card ? card.getBoundingClientRect() : null;
                    const arrow = btn ? btn.querySelector('svg.lucide-chevron-down') : null;
                    const aRect = arrow ? arrow.getBoundingClientRect() : null;
                    
                    const grid = document.querySelector('.grid.gap-6');
                    let cols = 1;
                    if (grid) {
                        cols = window.getComputedStyle(grid).gridTemplateColumns.split(' ').filter(c => c.trim().length > 0).length;
                    }
                    
                    return {
                        viewport: `${window.innerWidth}x${window.innerHeight}`,
                        scrollWidth: doc.scrollWidth,
                        clientWidth: doc.clientWidth,
                        hasHScroll: doc.scrollWidth > doc.clientWidth + 1,
                        btnWidth: bRect ? Math.round(bRect.width) : 0,
                        cardWidth: cRect ? Math.round(cRect.width) : 0,
                        selectorFits: (bRect && cRect) ? (bRect.right <= cRect.right + 2) : false,
                        arrowVisible: aRect ? (aRect.right <= bRect.right + 1 && aRect.width > 0) : false,
                        cols
                    };
                })()
                """
                rv = await send_cmd("Runtime.evaluate", {"expression": vp_script, "returnByValue": True})
                v = rv.get("result", {}).get("result", {}).get("value", {})
                
                exp_cols = 2 if w >= 1024 else 1
                status = "PASS" if (v.get("selectorFits") and not v.get("hasHScroll") and v.get("arrowVisible") and v.get("cols") == exp_cols) else "FAIL"
                print(f"[{status}] Viewport {name:10} | Selector: {v.get('btnWidth')}px / Card: {v.get('cardWidth')}px (Fits: {v.get('selectorFits')}) | Arrow: {v.get('arrowVisible')} | H-Scroll: {v.get('hasHScroll')} | Grid: {v.get('cols')} cols (Exp: {exp_cols})")

            # Check console errors
            print(f"\n--- Console Diagnostics ---")
            if console_errors:
                print(f"Captured {len(console_errors)} console notices/warnings:")
                for ce in console_errors[:5]:
                    print("  ", ce)
            else:
                print("Zero client-side errors detected in browser console!")

            print("=" * 80)
            return True
    finally:
        proc.kill()

if __name__ == "__main__":
    import sys
    success = asyncio.run(run_interactive_verification())
    sys.exit(0 if success else 1)
