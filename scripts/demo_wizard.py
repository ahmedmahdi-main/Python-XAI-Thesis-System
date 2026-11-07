"""Windows CPU setup/launch wizard. Uses a new venv, never the research environment."""

import argparse
from contextlib import contextmanager
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import struct
import subprocess
import sys
import time
from urllib.request import urlopen
import venv
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".demo_runtime"
PYTHON = ROOT / ".demo_venv/Scripts/python.exe"
STATE = RUNTIME / "server.json"
RUN_ID = "full_20261021T040901084647Z"
VALIDATION_ID = "validation_20261021T055002439194Z"
LOG = None


def say(message):
    print(message, flush=True)
    if LOG:
        LOG.write(message + "\n")
        LOG.flush()


def environment():
    search_path = os.pathsep.join(filter(None, [str(ROOT / "src"), os.environ.get("PYTHONPATH")]))
    return {**os.environ, "PYTHONUTF8": "1", "PYTHONPATH": search_path, "MPLCONFIGDIR": str(RUNTIME / "matplotlib"), "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false", "PYTHONHASHSEED": "42"}


def run(command):
    say("Running: " + subprocess.list2cmdline([str(x) for x in command]))
    with subprocess.Popen([str(x) for x in command], cwd=ROOT, env=environment(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace") as process:
        for line in process.stdout:
            say(line.rstrip())
        if process.wait():
            raise RuntimeError("The command above failed. Check its error and the diagnostic log, then run setup again.")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest(root=ROOT):
    manifest_path = root / "CPU_PACKAGE_MANIFEST.json"
    if not manifest_path.exists():
        say("Source checkout: package manifest absent; checking required research inventories instead.")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for relative, expected in manifest["files"].items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()):
            raise RuntimeError(f"Unsafe manifest path: {relative}")
        if not path.is_file() or path.stat().st_size != expected["bytes"] or sha256(path) != expected["sha256"]:
            raise RuntimeError(f"Package file missing or damaged: {relative}. Extract the verified ZIP again.")
    say(f"Integrity verified: {len(manifest['files'])} packaged files.")


def verify_artifacts():
    run_folder = ROOT / "artifacts/runs" / RUN_ID
    validation = ROOT / "artifacts/scientific_validation" / VALIDATION_ID
    required = [ROOT / "main.py", ROOT / "dashboard/app.py", ROOT / "artifacts/latest_full.json", run_folder / "run.json", run_folder / "inventory.json", validation / "protocol.json", validation / "new_metrics.csv", validation / "new_predictions.csv", validation / "offline_validation.html", ROOT / "docs/thesis_reported_reference.json", ROOT / "docs/THESIS_TRACEABILITY.md"]
    if not (run_folder / "run.json").exists():
        raise RuntimeError(f"Required saved experiment missing: {run_folder / 'run.json'}. Restore it from the original research backup; do not retrain to replace evidence.")
    metadata = json.loads((run_folder / "run.json").read_text(encoding="utf-8"))
    for asset in metadata["assets_completed"]:
        folder = run_folder / asset
        required.extend([ROOT / "data/raw" / f"{asset}.csv", ROOT / "data/manifests" / f"{asset}.json"])
        required.extend(folder / name for name in ["windows.npz", "data_audit.json", "training.json", "metrics.json", "predictions.csv", "next_forecast.json", "regimes.json", "LinearRegression.joblib", "RandomForest.joblib", "GradientBoosting.joblib", "LSTM/best.pt", "LSTM/last.pt", "LSTM/scalers.joblib"])
        for model in ["LinearRegression", "RandomForest", "GradientBoosting", "LSTM"]:
            required.extend(folder / model / "explanations" / name for name in ["quality.json", "shap.npz", "lime_local.png"])
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file() or not path.stat().st_size]
    if missing:
        raise RuntimeError("Required artifacts missing or empty:\n" + "\n".join(missing))
    for relative, expected in json.loads((run_folder / "inventory.json").read_text()).items():
        if sha256(run_folder / relative) != expected:
            raise RuntimeError(f"Saved research inventory mismatch: {run_folder / relative}")
    say(f"Required datasets, checkpoints, predictions and explanations found for {len(metadata['assets_completed'])} datasets.")


def runtime_check():
    code = "import json,sys,torch,streamlit,shap,lime,numpy,pandas,sklearn,plotly; assert sys.version_info[:2]==(3,12); assert torch.__version__=='2.5.1+cpu'; assert torch.version.cuda is None; print(json.dumps({'python':sys.version,'torch':torch.__version__,'cuda_available':torch.cuda.is_available()}))"
    run([PYTHON, "-c", code])


def process_stamp(pid):
    """Windows creation timestamp prevents reuse or stopping an unrelated recycled PID."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.c_void_p] * 4
    kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return None
    try:
        exit_code = ctypes.c_ulong()
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(exit_code)) or exit_code.value != 259:
            return None
        values = [ctypes.c_ulonglong() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *[ctypes.byref(value) for value in values]):
            return None
        return values[0].value
    finally:
        kernel.CloseHandle(handle)


def owned_state():
    try:
        state = json.loads(STATE.read_text())
        if state["root"] == str(ROOT.resolve()) and state.get("creation_stamp") is not None and state["creation_stamp"] == process_stamp(state["pid"]):
            return state
    except (OSError, ValueError, KeyError):
        pass
    return None


def terminate_owned_tree(state):
    """Find this exact process's descendants without WMI/taskkill privileges."""
    import signal
    from ctypes import wintypes

    class Entry(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD), ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG), ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR * 260)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    entries = []
    try:
        entry = Entry()
        entry.dwSize = ctypes.sizeof(entry)
        valid = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        while valid:
            entries.append((entry.th32ProcessID, entry.th32ParentProcessID))
            valid = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    selected = [(state["pid"], state["creation_stamp"])]
    for parent, _ in selected:
        for pid, parent_pid in entries:
            if parent_pid == parent and pid not in {p for p, _ in selected}:
                stamp = process_stamp(pid)
                if stamp is not None and stamp >= state["creation_stamp"]:
                    selected.append((pid, stamp))
    if process_stamp(state["pid"]) != state["creation_stamp"]:
        raise RuntimeError("Tracked server identity changed; refusing to stop any process.")
    for pid, stamp in reversed(selected):
        if process_stamp(pid) == stamp:
            os.kill(pid, signal.SIGTERM)


def healthy(port):
    try:
        with urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=2) as response:
            return response.status == 200 and response.read().strip() == b"ok"
    except OSError:
        return False


@contextmanager
def launch_lock(name="launcher.lock"):
    import msvcrt
    with (RUNTIME / name).open("a+b") as lock:
        lock.seek(0)
        lock.write(b"0")
        lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as error:
            raise RuntimeError("Another setup or launcher is running. Wait for it to finish, then retry.") from error
        try:
            yield
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


def start(port=8501, no_browser=False):
    if not PYTHON.is_file():
        raise RuntimeError("Run SETUP_DEMO.bat first. The isolated CPU environment is missing.")
    with launch_lock():
        state = owned_state()
        if state:
            if not healthy(state["port"]):
                raise RuntimeError("The existing demo process is not healthy. Run START_DEMO.bat stop, then start again. See its server log.")
            say(f"Dashboard already running; reusing {state['url']}")
            if not no_browser:
                webbrowser.open(state["url"])
            return state, True
        runtime_check()
        chosen = None
        for candidate in range(port, min(port + 20, 65536)):
            with socket.socket() as probe:
                try:
                    probe.bind(("127.0.0.1", candidate))
                    chosen = candidate
                    break
                except OSError:
                    say(f"Port {candidate} is occupied; leaving that service alone.")
        if chosen is None:
            raise RuntimeError(f"No free port between {port} and {min(port+19,65535)}. Close an unused service or pass --port NUMBER.")
        server_log = RUNTIME / "logs" / f"server_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.log"
        command = [str(PYTHON), "-m", "streamlit", "run", str(ROOT / "main.py"), "--server.address", "127.0.0.1", "--server.port", str(chosen), "--server.headless", "true", "--browser.gatherUsageStats", "false", "--server.fileWatcherType", "none"]
        say(f"Starting the original eight-tab dashboard on CPU at http://127.0.0.1:{chosen}")
        with server_log.open("w", encoding="utf-8") as output:
            process = subprocess.Popen(command, cwd=ROOT, env=environment(), stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)
        stamp = None
        for _ in range(20):
            stamp = process_stamp(process.pid)
            if stamp:
                break
            if process.poll() is not None:
                break
            time.sleep(.1)
        state = {"root": str(ROOT.resolve()), "pid": process.pid, "creation_stamp": stamp, "port": chosen, "url": f"http://127.0.0.1:{chosen}", "log": str(server_log)}
        STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        for _ in range(90):
            if process.poll() is not None:
                raise RuntimeError(f"Streamlit exited during startup. Read {server_log}")
            if healthy(chosen):
                say(f"Dashboard ready: {state['url']}\nServer log: {server_log}")
                if not no_browser:
                    webbrowser.open(state["url"])
                return state, False
            time.sleep(.5)
        raise RuntimeError(f"Streamlit did not become healthy in 45 seconds. Read {server_log}")


def stop():
    with launch_lock():
        state = owned_state()
        if state:
            # Terminate only this launcher's exact PID + creation time under this root.
            # Windows venv's python.exe can be a redirector with a child interpreter.
            # Stop the owned process tree so that the child cannot keep the port open.
            terminate_owned_tree(state)
            for _ in range(50):
                if not process_stamp(state["pid"]):
                    break
                time.sleep(.1)
            if process_stamp(state["pid"]):
                raise RuntimeError("The owned demo process did not stop; check its server log.")
            if healthy(state["port"]):
                raise RuntimeError("The old port still serves an application. Check the server log before restarting.")
            say("Stopped this folder's demo server.")
        else:
            say("No owned demo server is running.")
        STATE.unlink(missing_ok=True)


def setup(args):
    say("[1/7] Checking Windows, Python 3.12 and x64 compatibility")
    if platform.system() != "Windows" or sys.version_info[:2] != (3, 12) or struct.calcsize("P") != 8:
        raise RuntimeError("Install Windows x64 CPython 3.12 for your user, then run SETUP_DEMO.bat again. No CUDA or administrator account is required.")
    say("[2/7] Verifying package integrity and required research evidence")
    verify_manifest()
    verify_artifacts()
    say("[3/7] Preparing a separate local CPU environment (.demo_venv)")
    if not PYTHON.exists():
        venv.EnvBuilder(with_pip=True).create(PYTHON.parents[1])
    wheelhouse = ROOT / "wheelhouse-cpu"
    bundled = wheelhouse.is_dir() and any(wheelhouse.glob("torch-2.5.1+cpu-*.whl"))
    if args.offline and not bundled:
        raise RuntimeError("Offline CPU wheel bundle missing: wheelhouse-cpu/torch-2.5.1+cpu-*.whl. Use the complete CPU defense ZIP or run setup online.")
    say("[4/7] Detecting and installing missing CPU dependencies")
    install = [PYTHON, "-m", "pip", "install", "--disable-pip-version-check", "--no-compile", "--cache-dir", RUNTIME / "pip-cache"]
    if bundled:
        say("Using bundled Windows CPU wheels; internet is not needed.")
        install.extend(["--no-index", "--find-links", wheelhouse, "--only-binary=:all:"])
    else:
        say("CPU wheels are not bundled here; first installation needs internet access.")
    run([*install, "-r", ROOT / "requirements-cpu.txt"])
    project_wheels = sorted(wheelhouse.glob("xai_finance_thesis-*.whl")) if bundled else []
    if project_wheels:
        run([*install, "--no-deps", "--force-reinstall", project_wheels[-1]])
    else:
        run([*install, "--no-deps", "--force-reinstall", "--no-build-isolation", ROOT])
    run([PYTHON, "-m", "pip", "check"])
    say("[5/7] Checking imports, CPU checkpoint replay, metrics, SHAP and LIME")
    runtime_check()
    run([PYTHON, ROOT / "scripts/verify_cpu_replay.py", "--output", RUNTIME / "cpu_replay.json"])
    say("[6/7] Checking ports, actual dashboard rendering and server health")
    run([PYTHON, "-c", "from streamlit.testing.v1 import AppTest; app=AppTest.from_file('main.py',default_timeout=90).run(); assert not app.exception, app.exception; assert len(app.tabs)==8; assert app.title[0].value=='Financial forecasts, explained'; print('Original dashboard rendered: eight tabs, no exceptions')"])
    _, reused = start(args.port, no_browser=True)
    if not reused:
        stop()
    say("[7/7] Installation successful. Double-click START_DEMO.bat. Internet and CUDA are not required for the saved demonstration.")
    (RUNTIME / "setup_success.json").write_text(json.dumps({"status": "PASSED", "python": str(PYTHON), "offline_wheels": bundled, "completed_utc": datetime.now(timezone.utc).isoformat()}, indent=2), encoding="utf-8")


def main():
    global LOG
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["setup", "start", "stop", "verify-package"])
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    (RUNTIME / "logs").mkdir(parents=True, exist_ok=True)
    path = RUNTIME / "logs" / f"{args.action}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.log"
    with path.open("x", encoding="utf-8") as log:
        LOG = log
        try:
            if platform.system() != "Windows":
                raise RuntimeError("This wizard requires Windows x64.")
            if not 1024 <= args.port <= 65535:
                raise RuntimeError("Choose a local port between 1024 and 65535.")
            if args.action == "setup":
                with launch_lock("setup.lock"):
                    setup(args)
            elif args.action == "start":
                start(args.port, args.no_browser)
            elif args.action == "stop":
                stop()
            else:
                verify_manifest()
        except Exception as error:
            say(f"ERROR: {error}\nDiagnostic log: {path}")
            return 1
        finally:
            LOG = None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
