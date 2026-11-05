# شرح `scripts/test_deployment_cpu.py`

بصمة المصدر SHA-256: `8977f5c0b9b2b5fd3700e68e8241b96001df6f873845ead021085ff3c51c2693`.

لم يُنفذ اختبار النشر أو المتصفح في هذه الجلسة.

## الأسطر 1–12

```python
"""Execute Windows batch launch, duplicate/restart/occupied-port/offline checks."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
```

توثيق واستخدام argparse وimportlib وJSON والبيئة والمسار وsocket والعمليات وHTTP المحلي.

## الأسطر 15–24

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--port", type=int, default=8561)
    parser.add_argument("--setup", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    env = {**os.environ, "XAI_DEMO_NO_PAUSE": "1", "XAI_TEST_OFFLINE": "1", "PYTHONPATH": str(root / "scripts/offline_guard"), "PYTHONUTF8": "1"}
    output = root / ".demo_runtime/acceptance"
    output.mkdir(parents=True, exist_ok=True)
```

main تقرأ الجذر والمنفذ وخيار setup وتجهز بيئة اختبار دون pause وحارس شبكة Python، وتنشئ مجلد acceptance.

## الأسطر 26–34

```python
    def batch(name, *options, check=True):
        command = ["cmd.exe", "/d", "/c", str(root / name), *options]
        result = subprocess.run(command, cwd=root, env=env, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900)
        print(result.stdout, flush=True)
        with (output / "batch.log").open("a", encoding="utf-8") as stream:
            stream.write(result.stdout)
        if check:
            assert result.returncode == 0, result.stdout
        return result
```

الدالة الداخلية batch تشغل ملف Windows عبر cmd بمهلة 900 ثانية وتسجل خرجه وتؤكد نجاحه إن طلب check، وتعيد النتيجة.

## الأسطر 36–41

```python
    if args.setup:
        batch("SETUP_DEMO.bat", "--offline")
    python = root / ".demo_venv/Scripts/python.exe"
    guard = subprocess.run([str(python), "-c", "import socket; socket.create_connection(('example.com',443),timeout=2)"], env=env, capture_output=True, text=True)
    assert guard.returncode != 0 and "Offline acceptance test denied" in guard.stderr
    receipt = {"status": "PASSED", "root": str(root), "offline_setup_executed": args.setup, "external_python_network_guard_verified": True}
```

عند طلب setup تنفذ التثبيت offline؛ تختبر أن اتصال Python خارجي محظور وتبدأ الإيصال. يتطلب Python البيئة الموجودة.

## الأسطر 42–54

```python
    with socket.socket() as occupant:
        occupant.bind(("127.0.0.1", args.port))
        occupant.listen()
        first = batch("START_DEMO.bat", "--no-browser", "--port", str(args.port))
        assert "occupied" in first.stdout
        state = json.loads((root / ".demo_runtime/server.json").read_text())
        assert state["port"] == args.port + 1
        with urlopen(state["url"] + "/_stcore/health") as response:
            assert response.read() == b"ok"
        batch("START_DEMO.bat", "--no-browser", "--port", str(args.port))
        assert json.loads((root / ".demo_runtime/server.json").read_text())["pid"] == state["pid"]
        receipt["occupied_port"] = {"occupied": args.port, "selected": state["port"], "existing_service_preserved": occupant.getsockname()[1] == args.port}
        receipt["duplicate_start_reused_pid"] = state["pid"]
```

تحجز المنفذ، وتطلق العرض في منفذ تالٍ وتفحص الصحة وإعادة استخدام PID عند البدء المكرر، وتوثق بقاء خدمة المنفذ المشغول.

## الأسطر 55–66

```python
        # Exercise the default browser-opening branch using a recorded callback.
        spec = importlib.util.spec_from_file_location("tested_wizard", root / "scripts/demo_wizard.py")
        wizard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wizard)
        opened = []
        wizard.webbrowser.open = lambda url: opened.append(url)
        _, reused = wizard.start(args.port)
        assert reused and opened == [state["url"]]
        receipt["browser_open_callback"] = opened
        invalid = batch("START_DEMO.bat", "--no-browser", "--port", "80", check=False)
        assert invalid.returncode != 0 and "between 1024 and 65535" in invalid.stdout
        receipt["invalid_port_actionable_error"] = True
```

تحمل wizard ديناميكياً وتستبدل webbrowser.open برد مسجل لاختبار فرع فتح المتصفح ثم تفحص رفض منفذ 80.

## الأسطر 67–78

```python
        appcheck = subprocess.run([str(python), str(root / "scripts/check_dashboard_cpu.py"), "--output", str(output / "dashboard.json")], cwd=root, env=env, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
        print(appcheck.stdout, flush=True)
        assert appcheck.returncode == 0
        batch("START_DEMO.bat", "stop")
        batch("START_DEMO.bat", "--no-browser", "--port", str(args.port))
        restarted = json.loads((root / ".demo_runtime/server.json").read_text())
        assert restarted["pid"] != state["pid"]
        receipt["restart_new_pid"] = restarted["pid"]
        # Leave the tested server running for the subsequent browser smoke.
        receipt["running_url"] = restarted["url"]
    (output / "deployment.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print("DEPLOYMENT ACCEPTANCE PASSED:", receipt["running_url"], flush=True)
```

تشغل اختبار الواجهة وتوقف الخادم وتعيد تشغيله وتتحقق من تغير PID وتترك الخادم للاختبار التالي، ثم تكتب الإيصال. التنفيذ يبدأ ويوقف عمليات ويكتب آثاراً؛ لم ينفذ هنا.

## الأسطر 81–82

```python
if __name__ == "__main__":
    main()
```

حارس التشغيل يستدعي main.
