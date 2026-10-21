import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.address", "127.0.0.1", "--server.port", "8501", "--browser.gatherUsageStats", "false"], cwd=ROOT, check=True)
