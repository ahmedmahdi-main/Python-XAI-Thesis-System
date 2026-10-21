from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
python = ROOT / ".defense_venv/Scripts/python.exe"
if not python.exists():
    subprocess.run([sys.executable, str(ROOT / "scripts/setup_offline.py")], cwd=ROOT, check=True)
subprocess.run([str(python), str(ROOT / "scripts/launch_demo.py")], cwd=ROOT, check=True)
