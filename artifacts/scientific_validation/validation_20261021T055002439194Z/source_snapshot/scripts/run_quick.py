import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ["PYTHONHASHSEED"] = "42"
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
subprocess.run([sys.executable, "-m", "xai_finance.cli", "all", "--config", "configs/quick_demo.yaml"], cwd=ROOT, check=True)
