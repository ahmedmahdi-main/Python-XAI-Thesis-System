"""Install the pinned project in a fresh local venv exclusively from bundled wheels."""

from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]
environment = ROOT / ".defense_venv"
if sys.version_info[:2] != (3, 12):
    raise RuntimeError("Bundled Windows AMD64 wheels require CPython 3.12")
venv.EnvBuilder(with_pip=True).create(environment)
python = environment / "Scripts/python.exe"
subprocess.run([str(python), "-m", "pip", "install", "--no-index", "--find-links", str(ROOT / "wheelhouse"), "-r", str(ROOT / "requirements-lock.txt"), "--disable-pip-version-check"], cwd=ROOT, check=True)
project_wheel = next((ROOT / "wheelhouse").glob("xai_finance_thesis-*.whl"))
subprocess.run([str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(project_wheel)], cwd=ROOT, check=True)
subprocess.run([str(python), "-m", "pip", "check"], cwd=ROOT, check=True)
print("Offline environment ready:", python)
