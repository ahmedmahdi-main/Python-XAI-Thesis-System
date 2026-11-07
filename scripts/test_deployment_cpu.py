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

    def batch(name, *options, check=True):
        command = ["cmd.exe", "/d", "/c", str(root / name), *options]
        result = subprocess.run(command, cwd=root, env=env, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900)
        print(result.stdout, flush=True)
        with (output / "batch.log").open("a", encoding="utf-8") as stream:
            stream.write(result.stdout)
        if check:
            assert result.returncode == 0, result.stdout
        return result

    if args.setup:
        batch("SETUP_DEMO.bat", "--offline")
    python = root / ".demo_venv/Scripts/python.exe"
    guard = subprocess.run([str(python), "-c", "import socket; socket.create_connection(('example.com',443),timeout=2)"], env=env, capture_output=True, text=True)
    assert guard.returncode != 0 and "Offline acceptance test denied" in guard.stderr
    receipt = {"status": "PASSED", "root": str(root), "offline_setup_executed": args.setup, "external_python_network_guard_verified": True}
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


if __name__ == "__main__":
    main()
