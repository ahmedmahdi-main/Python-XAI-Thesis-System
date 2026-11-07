"""Compatibility command for the CPU-only offline setup wizard."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
raise SystemExit(subprocess.call([sys.executable, str(ROOT / "scripts/demo_wizard.py"), "setup", "--offline", *sys.argv[1:]], cwd=ROOT))
