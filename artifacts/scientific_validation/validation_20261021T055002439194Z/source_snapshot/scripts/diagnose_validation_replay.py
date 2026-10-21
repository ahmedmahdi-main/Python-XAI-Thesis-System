"""Measure cross-device error before choosing a precision-aware replay criterion."""
import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from xai_finance.models.lstm_model import load_lstm
from xai_finance.pipelines.train import load_windows
from xai_finance.seed import seed_experiment
from xai_finance.storage import read_json, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    destination = parser.parse_args().folder.resolve()
    seed_experiment(42)
    diagnostics = []
    for path in sorted((destination / "experiments").rglob("design.json")):
        design = read_json(path)
        windows = load_windows(Path(design["input_windows_source"]).parent)
        with np.load(path.parent / "target_and_partitions.npz") as saved:
            fixture = windows.flat[saved["test"]]
        table = pd.read_csv(path.parent / "predictions.csv", float_precision="round_trip")
        recorded = table.loc[table.model == "LSTM", "predicted_target"].to_numpy()
        scalers = joblib.load(path.parent / "LSTM/scalers.joblib")
        cpu = load_lstm(path.parent / "LSTM", scalers, "cpu").predict(fixture)
        gpu = load_lstm(path.parent / "LSTM", scalers, "cuda").predict(fixture)
        np.testing.assert_array_equal(gpu, recorded)
        diagnostics.append({**{name: design[name] for name in ["asset", "target", "design", "fold"]}, "cuda_replay_bitwise_equal": bool(np.array_equal(gpu, recorded)), "cpu_max_abs_error_target_units": float(np.max(np.abs(cpu - recorded))), "training_target_scale": float(scalers.target.scale_[0]), "cpu_max_error_training_std_units": float(np.max(np.abs(cpu - recorded)) / scalers.target.scale_[0])})
    write_json(destination / "cross_device_diagnostics.json", diagnostics)
    print(pd.DataFrame(diagnostics).to_string(index=False))


if __name__ == "__main__":
    main()
