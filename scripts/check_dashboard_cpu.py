"""Exercise the original eight tabs with external Python connections denied."""

import argparse
import json
from pathlib import Path
import socket

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/deployment/dashboard.json")
    args = parser.parse_args()
    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex

    def check(address):
        if isinstance(address, tuple) and address[0] not in {"localhost", "127.0.0.1", "::1"}:
            raise RuntimeError(f"External connection denied during offline test: {address}")

    def connect(connection, address):
        check(address)
        return original_connect(connection, address)

    def connect_ex(connection, address):
        check(address)
        return original_connect_ex(connection, address)

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    app = AppTest.from_file(str(ROOT / "main.py"), default_timeout=90).run()
    assert not app.exception, app.exception
    assert app.title[0].value == "Financial forecasts, explained"
    assert len(app.tabs) == 8
    receipt = {"status": "PASSED", "external_python_connections": "denied", "tabs": [t.label for t in app.tabs], "experiments": []}
    runs = list(app.selectbox(key="run").options)
    for run in runs:
        selected_run = next(p for p in app.selectbox(key="run").value.parent.iterdir() if p.name == run)
        app.selectbox(key="run").set_value(selected_run).run()
        assert not app.exception, app.exception
        assets = list(app.selectbox(key="asset").options)
        for asset in assets:
            app.selectbox(key="asset").set_value(asset).run()
            assert not app.exception, app.exception
            for model in ["LinearRegression", "RandomForest", "GradientBoosting", "LSTM"]:
                app.selectbox(key="forecast_model").set_value(model)
                app.selectbox(key="explain_model").set_value(model).run()
                assert not app.exception, app.exception
                dates = app.selectbox(key="explanation_date").options
                for date in {dates[0], dates[-1]}:
                    app.selectbox(key="explanation_date").set_value(date).run()
                    assert not app.exception, app.exception
                assert len(app.dataframe) >= 6
            print(f"PASS {run}/{asset}: four forecasts, paired SHAP/LIME, eight tabs", flush=True)
        receipt["experiments"].append({"run": run, "datasets": assets, "models_per_dataset": 4, "explanation_dates": "first and last for each model"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
