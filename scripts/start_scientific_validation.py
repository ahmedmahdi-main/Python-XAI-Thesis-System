"""Freeze an inventory and protocol before running additional experiments."""
from datetime import datetime, timezone
from pathlib import Path

from xai_finance.config import ROOT
from xai_finance.storage import sha256, write_json


def protected_files() -> list[Path]:
    excluded = {".venv", ".offline_verify", ".idea", ".pytest_cache", ".ruff_cache", "__pycache__", "build", "provider_cache", "scientific_validation"}
    return sorted(path for path in ROOT.rglob("*") if path.is_file() and not excluded.intersection(path.relative_to(ROOT).parts))


def main() -> None:
    inventory = {str(path.relative_to(ROOT)): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in protected_files()}
    run_id = "validation_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder = ROOT / "artifacts/scientific_validation" / run_id
    folder.mkdir(parents=True, exist_ok=False)
    write_json(folder / "preservation_before.json", inventory)
    protocol = {
        "validation_id": run_id, "original_run": "full_20261021T040901084647Z",
        "created_utc": datetime.now(timezone.utc).isoformat(), "seed": 42,
        "status": "EXPLORATORY: original test results already observed; no new independent holdout",
        "fixed_split": {"price_change": ["AAPL", "SP500", "NASDAQ", "GOLD", "OIL"], "simple_return": ["AAPL", "SP500", "NASDAQ", "GOLD"]},
        "return_exclusion": "OIL has a negative historical price; price_change retains every oil observation; no return filtering or clipping",
        "features": "Exact frozen 30x20 windows; target-only controlled comparison; no feature search",
        "targets": {"price_change": "P[t+1]-P[t]", "simple_return": "P[t+1]/P[t]-1"},
        "reconstruction": {"price_change": "P[t]+predicted_change", "simple_return": "P[t]*(1+predicted_return)"},
        "models": ["LinearRegression", "RandomForest", "GradientBoosting", "LSTM"],
        "tabular_search": "Same two RF and GBM candidates as frozen run; validation target RMSE; training-only fits; no final refit",
        "lstm": {"epochs": 60, "patience": 8, "hidden_size": 32, "dropout": 0.1, "learning_rate": 0.001, "batch_candidates": [32, 64], "amp": True, "device": "auto", "effective_lookback": 30},
        "baselines": ["Zero", "TrainMean", "LastObservedChangeOrReturn", "TrainMajorityDirectionMedianMagnitude"],
        "walk_forward": {"assets": ["AAPL", "SP500"], "target": "price_change", "folds": 3, "test": "Three contiguous disjoint blocks covering original test period", "fit": "Expanding history; latest 270 pre-block observations for validation; all earlier observations for training; no test fitted preprocessing", "lstm_epochs": 30},
        "direction": "Three-way sign accuracy, nonzero prediction coverage and conditional hit rate; binary-up accuracy also reported with zero treated as not-up",
        "uncertainty": "Paired circular block bootstrap of price squared-error difference versus Zero, block length 10, 2000 draws, seeded; exploratory unadjusted 95% intervals",
        "restrictions": "No tuning after seeing new test results; no edits to original run, snapshots, source, checkpoints or offline package",
    }
    write_json(folder / "protocol.json", protocol)
    print(folder)
    print(f"Protected files: {len(inventory)}; protocol SHA256: {sha256(folder / 'protocol.json')}")


if __name__ == "__main__":
    main()
