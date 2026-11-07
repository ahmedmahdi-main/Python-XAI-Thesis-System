"""Real Edge browser acceptance via CDP; no Selenium/Playwright dependency.

Browser external HTTP(S) is sent to a closed loopback proxy; local app bypasses it.
"""

import argparse
import base64
import json
from pathlib import Path
import subprocess
import time
from urllib.request import urlopen

from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[1]


class CDP:
    def __init__(self, url):
        self.ws = connect(url, max_size=32 * 1024 * 1024, proxy=None, legacy=True)
        self.number = 0
        self.errors = []

    def call(self, method, params=None):
        self.number += 1
        number = self.number
        self.ws.send(json.dumps({"id": number, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self.ws.recv(timeout=60))
            if message.get("method") == "Runtime.exceptionThrown":
                self.errors.append(message["params"])
            if message.get("id") == number:
                if "error" in message:
                    raise RuntimeError(message["error"])
                return message.get("result", {})

    def evaluate(self, expression):
        result = self.call("Runtime.evaluate", {"expression": expression, "returnByValue": True, "awaitPromise": True})
        if "exceptionDetails" in result:
            raise RuntimeError(result["exceptionDetails"])
        return result.get("result", {}).get("value")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8511")
    parser.add_argument("--debug-port", type=int, default=9228)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/deployment/browser")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    edge = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
    if not edge.exists():
        raise RuntimeError("Microsoft Edge is required for this developer browser test.")
    profile = args.output / "profile"
    with (args.output / "edge.log").open("w") as log:
        process = subprocess.Popen([str(edge), "--headless=new", "--no-sandbox", "--disable-gpu", "--no-first-run", "--disable-background-networking", "--disable-quic", "--proxy-server=http://127.0.0.1:9", "--proxy-bypass-list=localhost;127.0.0.1;[::1]", f"--remote-debugging-port={args.debug_port}", f"--user-data-dir={profile}", "about:blank"], creationflags=0x08000000, stdout=log, stderr=log)
        browser = None
        try:
            for _ in range(60):
                try:
                    with urlopen(f"http://127.0.0.1:{args.debug_port}/json/version", timeout=2) as response:
                        version = json.load(response)
                    break
                except OSError:
                    time.sleep(.5)
            else:
                raise RuntimeError("Edge did not expose its developer port; see edge.log")
            browser = CDP(version["webSocketDebuggerUrl"])
            browser.call("Target.createTarget", {"url": args.url})
            with urlopen(f"http://127.0.0.1:{args.debug_port}/json/list") as response:
                target = next(t for t in json.load(response) if t.get("url", "").startswith(args.url))
            page = CDP(target["webSocketDebuggerUrl"])
            page.call("Runtime.enable")
            page.call("Page.enable")
            page.call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 1050, "deviceScaleFactor": 1, "mobile": False})
            for _ in range(120):
                if page.evaluate("document.querySelectorAll('[role=tab]').length") == 8:
                    break
                time.sleep(.5)
            else:
                raise AssertionError(page.evaluate("document.body.innerText"))
            time.sleep(2)
            tabs = page.evaluate("Array.from(document.querySelectorAll('[role=tab]')).map(x=>x.innerText)")
            expected = ["A forecast with an evidence trail", "What the model could know", "Actual", "mae", "LIME local surrogate", "A priori regime", "local artifacts", "THESIS_REPORTED_NOT_REPRODUCED"]
            for index, label in enumerate(tabs):
                page.evaluate(f"document.querySelectorAll('[role=tab]')[{index}].click()")
                time.sleep(.3)
                visible = page.evaluate("Array.from(document.querySelectorAll('[role=tabpanel]')).filter(x=>!x.hidden&&x.getBoundingClientRect().height>0).map(x=>x.innerText).join('\\n')")
                assert expected[index] in visible, (label, visible)
                assert not page.evaluate("document.querySelector('[data-testid=stException]') !== null")
                if index == 6:
                    page.evaluate("Array.from(document.querySelectorAll('summary')).find(x=>x.innerText.includes('Saved scientific validation results')).click()")
                    time.sleep(.3)
                    assert page.evaluate("document.body.innerText.includes('EXPLORATORY: original test results already observed')")
                    assert page.evaluate("document.body.innerText.includes('Download standalone offline validation page')")
                shot = page.call("Page.captureScreenshot", {"format": "png"})
                (args.output / f"tab_{index+1}.png").write_bytes(base64.b64decode(shot["data"]))
                print(f"BROWSER PASS: {label}", flush=True)
            text = page.evaluate("document.body.innerText")
            assert "Financial forecasts, explained" in text
            assert not page.errors, page.errors
            receipt = {"status": "PASSED", "browser": version["Browser"], "url": args.url, "tabs_clicked_and_content_checked": tabs, "scientific_validation_expanded": True, "javascript_exceptions": page.errors, "external_browser_http": "closed loopback proxy; localhost bypass only", "screenshots": 8}
            (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
            page.ws.close()
        finally:
            if browser:
                try:
                    browser.call("Browser.close")
                except Exception:
                    pass
            if process.poll() is None:
                process.terminate()


if __name__ == "__main__":
    main()
