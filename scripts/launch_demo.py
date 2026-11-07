import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
raise SystemExit(subprocess.call([sys.executable, str(ROOT / "scripts/demo_wizard.py"), "start", *sys.argv[1:]], cwd=ROOT))
