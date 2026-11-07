"""Stable Streamlit entry point for the original saved-evidence dashboard.

Run with ``python -m streamlit run main.py`` or START_DEMO.bat.
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "dashboard" / "app.py"), run_name="__main__")
