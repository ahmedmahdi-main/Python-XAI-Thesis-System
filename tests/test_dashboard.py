from pathlib import Path
import shutil

from streamlit.testing.v1 import AppTest


def test_missing_artifacts_shows_actionable_setup_commands(tmp_path):
    project = Path(__file__).resolve().parents[1]
    dashboard = tmp_path / "dashboard"
    dashboard.mkdir()
    shutil.copy2(project / "dashboard/app.py", dashboard / "app.py")
    app = AppTest.from_file(str(dashboard / "app.py")).run(timeout=30)
    assert not app.exception
    assert any("No saved experiment" in message.value for message in app.info)
    assert "xai_finance.cli train" in app.code[0].value
