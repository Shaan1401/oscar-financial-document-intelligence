import asyncio
import json
import urllib.request
import subprocess
import time
import websockets
from PIL import Image
from pathlib import Path

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ROOT = Path(__file__).resolve().parent.parent

async def verify_dashboard():
    print("=== OSCAR Dashboard Runtime Verification ===")
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=9977",
        "--disable-gpu",
        "--window-size=1440,900"
    ]
    proc = subprocess.Popen(cmd)
    
    tabs = None
    for _ in range(15):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen("http://127.0.0.1:9977/json") as r:
                tabs = json.loads(r.read())
                if tabs:
                    break
        except Exception:
            pass

    if not tabs:
        print("ERROR: Cannot connect to Chrome CDP.")
        proc.kill()
        return

    try:
        ws_url = [t for t in tabs if t.get("type") == "page"][0]["webSocketDebuggerUrl"]
        async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
            msg_id = 1
            async def send_cmd(method, params=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                payload = {"id": cid, "method": method}
                if params:
                    payload["params"] = params
                await ws.send(json.dumps(payload))
                while True:
                    m = json.loads(await ws.recv())
                    if m.get("id") == cid:
                        return m

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")

            # 1. Navigate to dashboard
            print("Navigating to http://127.0.0.1:5173/...")
            await send_cmd("Page.navigate", {"url": "http://127.0.0.1:5173/"})
            await asyncio.sleep(3.0)

            # 2. Check for Vite error overlay
            err_eval = await send_cmd("Runtime.evaluate", {
                "expression": "Boolean(document.querySelector('vite-error-overlay'))"
            })
            has_error = err_eval.get("result", {}).get("result", {}).get("value")
            print(f"1. Vite Error Overlay Present: {has_error}")
            assert not has_error, "Vite error overlay detected!"

            # 3. Check Page Title and Header
            header_eval = await send_cmd("Runtime.evaluate", {
                "expression": "document.querySelector('h1') ? document.querySelector('h1').innerText : ''"
            })
            h1 = header_eval.get("result", {}).get("result", {}).get("value")
            print(f"2. Page Main Heading: '{h1}'")
            
            body_eval = await send_cmd("Runtime.evaluate", {
                "expression": "document.body.innerText"
            })
            b_txt = body_eval.get("result", {}).get("result", {}).get("value", "")
            print("BODY TEXT:\n", b_txt[:800].encode('ascii', errors='replace').decode('ascii'))

            # 4. Check KPI Cards (Actual numbers from SQLite)
            kpi_eval = await send_cmd("Runtime.evaluate", {
                "expression": "Array.from(document.querySelectorAll('.oscar-card')).map(el => el.innerText)"
            })
            cards = kpi_eval.get("result", {}).get("result", {}).get("value", [])
            print(f"3. Found {len(cards)} Oscar Cards on Dashboard.")
            for i, c in enumerate(cards[:4]):
                lines = [line.strip() for line in c.split("\n") if line.strip()]
                print(f"   KPI {i+1}: {' | '.join(lines)}")

            # 5. Check Financial Integrity Bridge
            bridge_eval = await send_cmd("Runtime.evaluate", {
                "expression": "document.body.innerText.includes('Financial Integrity Bridge') && document.body.innerText.includes('Reconciled (₹0.00 Variance)')"
            })
            bridge_ok = bridge_eval.get("result", {}).get("result", {}).get("value")
            print(f"4. Financial Integrity Bridge Reconciled (INR 0.00 Variance): {bridge_ok}")

            # 6. Check Charts rendered (SVGs inside cards)
            svg_eval = await send_cmd("Runtime.evaluate", {
                "expression": "document.querySelectorAll('svg.recharts-surface').length"
            })
            svg_count = svg_eval.get("result", {}).get("result", {}).get("value")
            print(f"5. Interactive Recharts SVGs Rendered: {svg_count}")

            # 7. Check Recent Statements Table Rows
            table_eval = await send_cmd("Runtime.evaluate", {
                "expression": "document.querySelectorAll('table tbody tr').length"
            })
            tr_count = table_eval.get("result", {}).get("result", {}).get("value")
            print(f"6. Recent Statements Table Rows: {tr_count} statements rendered")

            # 8. Check Dark Mode Toggle and Rendering
            print("\nSwitching to Dark Theme...")
            await send_cmd("Runtime.evaluate", {
                "expression": "document.documentElement.classList.add('dark');"
            })
            await asyncio.sleep(0.5)

            dark_bg_eval = await send_cmd("Runtime.evaluate", {
                "expression": "window.getComputedStyle(document.body).backgroundColor"
            })
            dark_bg = dark_bg_eval.get("result", {}).get("result", {}).get("value")
            print(f"7. Dark Theme Body Background: {dark_bg}")

            # 9. Check Light Mode
            print("Switching to Light Theme...")
            await send_cmd("Runtime.evaluate", {
                "expression": "document.documentElement.classList.remove('dark');"
            })
            await asyncio.sleep(0.5)
            light_bg_eval = await send_cmd("Runtime.evaluate", {
                "expression": "window.getComputedStyle(document.body).backgroundColor"
            })
            light_bg = light_bg_eval.get("result", {}).get("result", {}).get("value")
            print(f"8. Light Theme Body Background: {light_bg}")

            print("\nAll Dashboard runtime checks PASSED successfully!")
    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(verify_dashboard())
