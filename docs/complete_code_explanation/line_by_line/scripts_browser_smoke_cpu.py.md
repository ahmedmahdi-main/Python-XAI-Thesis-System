# شرح `scripts/browser_smoke_cpu.py`

بصمة المصدر SHA-256: `feb83a0e6fd44b841d381d7b8d6142612cf60dc6db4345819fadf560ab71bdba`.

لم يُنفذ اختبار النشر أو المتصفح في هذه الجلسة.

## الأسطر 1–16

```python
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
```

توثيق تجربة Edge ووكيل loopback، واستيرادات الأدوات القياسية وwebsockets الخارجية وتعريف الجذر.

## الأسطر 19–23

```python
class CDP:
    def __init__(self, url):
        self.ws = connect(url, max_size=32 * 1024 * 1024, proxy=None, legacy=True)
        self.number = 0
        self.errors = []
```

CDP ينشئ اتصال WebSocket إلى بروتوكول تصحيح المتصفح ويبدأ عداد الرسائل وقائمة الأخطاء.

## الأسطر 25–36

```python
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
```

call يزيد المعرف ويرسل طلب JSON ويستقبل حتى يجد الاستجابة المطابقة، ويسجل استثناءات Runtime ويرفع خطأ البروتوكول؛ timeout الاستقبال 60 ثانية.

## الأسطر 38–42

```python
    def evaluate(self, expression):
        result = self.call("Runtime.evaluate", {"expression": expression, "returnByValue": True, "awaitPromise": True})
        if "exceptionDetails" in result:
            raise RuntimeError(result["exceptionDetails"])
        return result.get("result", {}).get("value")
```

evaluate تنفذ تعبير JavaScript عبر CDP وتعيد القيمة أو ترفع تفاصيل الاستثناء.

## الأسطر 45–58

```python
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
```

main تقرأ رابط التطبيق ومنفذ التصحيح والوجهة، وتنشئ الوجهة وتطلب Edge في المسار الثابت، ثم تطلقه headless بملف شخصي ووكيل خارجي إلى منفذ loopback مغلق واستثناء localhost؛ لا يثبت ذلك منع كل بروتوكول شبكة.

## الأسطر 59–77

```python
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
```

تنتظر منفذ المطور وتفتح اتصال CDP وهدف التطبيق وتحدد الصفحة وتمكن Runtime وPage وتحاكي نافذة 1440×1050.

## الأسطر 78–92

```python
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
```

تنتظر ثمانية تبويبات وتضغط كلاً منها وتتحقق من نص ظاهر وعدم وجود stException؛ انتظار الزمن الثابت قد يتأثر بسرعة الجهاز.

## الأسطر 93–105

```python
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
```

في تبويب إعادة الإنتاج توسع التحقق العلمي وتتحقق من النص وأزرار التنزيل، وتلتقط PNG لكل تبويب ثم تفحص العنوان واستثناءات JS وتكتب إيصالاً.

## الأسطر 106–114

```python
            page.ws.close()
        finally:
            if browser:
                try:
                    browser.call("Browser.close")
                except Exception:
                    pass
            if process.poll() is None:
                process.terminate()
```

تغلق قناة الصفحة وتحاول إغلاق المتصفح في finally ثم تنهي العملية إن بقيت؛ تترك صوراً وسجلات وملف profile في الوجهة.

## الأسطر 117–118

```python
if __name__ == "__main__":
    main()
```

حارس التشغيل. لم يشغل المتصفح هنا.
