"""Find an already-installed x64 Python 3.12; never download a runtime implicitly."""

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
check = "import sys,struct; assert sys.version_info[:2]==(3,12) and struct.calcsize('P')==8"
candidates = [Path(os.environ["XAI_PYTHON"])] if os.environ.get("XAI_PYTHON") else []
candidates.append(Path(sys.executable))
for variable in ["APPDATA", "LOCALAPPDATA"]:
    if os.environ.get(variable):
        folder = Path(os.environ[variable]) / "uv/python"
        candidates.extend(sorted(folder.glob("cpython-3.12*-windows-x86_64-none/python.exe"), reverse=True))
if os.environ.get("UV_PYTHON_INSTALL_DIR"):
    candidates.extend(sorted(Path(os.environ["UV_PYTHON_INSTALL_DIR"]).glob("cpython-3.12*-windows-x86_64-none/python.exe"), reverse=True))
for python in dict.fromkeys(candidates):
    if python.is_file() and subprocess.run([str(python), "-c", check], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        raise SystemExit(subprocess.call([str(python), str(ROOT / "scripts/demo_wizard.py"), "setup", *sys.argv[1:]], cwd=ROOT))
print("Windows x64 Python 3.12 was not found. Install it for your user, then rerun SETUP_DEMO.bat.")
print("If it is installed in a custom location, set XAI_PYTHON to its full python.exe path.")
raise SystemExit(1)
