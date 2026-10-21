from dataclasses import replace
import gc
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
from threadpoolctl import threadpool_limits

from xai_finance.models.lstm_model import fit_lstm
from xai_finance.models.sklearn_models import candidates, fit_candidates
from xai_finance.pipelines.train import load_windows, software_environment, split_manifest, verify_reload
from xai_finance.seed import seed_experiment
from xai_finance.storage import read_json, sha256, write_json
from xai_finance.validation.design import implied_prices, naive_predictions, transformed_windows, walk_forward_partitions
from xai_finance.validation.statistics import evaluation_metrics


def fit_models(windows, configuration: dict, folder: Path) -> tuple[dict, dict]:
    models, audits = {}, {}
    for name, estimators in candidates(configuration).items():
        print(f"{folder.name}: fitting {name}", flush=True)
        models[name], audits[name] = fit_candidates(estimators, windows)
        joblib.dump(models[name], folder / f"{name}.joblib")
    models["LSTM"], audits["LSTM"] = fit_lstm(windows, configuration, folder / "LSTM")
    joblib.dump(models["LSTM"].scalers, folder / "LSTM/scalers.joblib")
    return models, audits


def predictions_table(windows, specification: dict, models: dict) -> pd.DataFrame:
    test, target = windows.partitions["test"], specification["target"]
    predictions = {name: model.predict(windows.flat[test]) for name, model in models.items()}
    predictions.update(naive_predictions(windows, target))
    transformed = transformed_windows(windows, target)
    tables = []
    for name, predicted in predictions.items():
        tables.append(pd.DataFrame({**specification, "model": name, "feature_cutoff": windows.origins[test], "target_date": windows.targets[test], "current_price": windows.current_close[test], "actual_price": windows.y[test], "predicted_price": implied_prices(predicted, windows.current_close[test], target), "actual_target": transformed.y[test], "predicted_target": predicted}))
    return pd.concat(tables, ignore_index=True)


def job_configuration(protocol: dict, specification: dict) -> dict:
    configuration = {**protocol["lstm"], "seed": protocol["seed"], "trees": 100, "search": True}
    if specification["design"] == "walk_forward":
        configuration["epochs"] = protocol["walk_forward"]["lstm_epochs"]
    return configuration


def experiment_job(windows, specification: dict, context: dict) -> None:
    folder = context["destination"] / "experiments" / specification["design"] / specification["target"] / f"{specification['asset']}_fold{specification['fold']}"
    if (folder / "completion.json").exists():
        previous = read_json(folder / "completion.json")
        for name, digest in previous["files"].items():
            assert sha256(folder / name) == digest, f"Completed job changed: {folder / name}"
        print(f"Verified completed job: {folder}", flush=True)
        return
    folder.mkdir(parents=True, exist_ok=False)
    seed_experiment(context["protocol"]["seed"])
    target_windows = transformed_windows(windows, specification["target"])
    configuration = job_configuration(context["protocol"], specification)
    write_json(folder / "design.json", {**specification, "configuration": configuration, "split": split_manifest(windows), "target_definition": context["protocol"]["targets"][specification["target"]], "input_windows_source": str(context["original"] / specification["asset"] / "windows.npz"), "input_windows_sha256": sha256(context["original"] / specification["asset"] / "windows.npz")})
    np.savez_compressed(folder / "target_and_partitions.npz", y=target_windows.y, origins=windows.origins.asi8, targets=windows.targets.asi8, **windows.partitions)
    models, training = fit_models(target_windows, configuration, folder)
    write_json(folder / "training.json", training)
    verify_reload(folder, models, target_windows)
    table = predictions_table(windows, specification, models)
    table.to_csv(folder / "predictions.csv", index=False)
    metric_rows = [{**specification, "model": name, **evaluation_metrics(group)} for name, group in table.groupby("model", sort=False)]
    write_json(folder / "metrics.json", metric_rows)
    write_json(folder / "completion.json", {"files": {str(path.relative_to(folder)): sha256(path) for path in folder.rglob("*") if path.is_file()}, "status": "EXECUTED_AND_CPU_RELOAD_VERIFIED"})
    print(pd.DataFrame(metric_rows)[["asset", "model", "rmse", "rmse_ratio_vs_zero", "direction_accuracy"]].to_string(index=False), flush=True)
    del models
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def run_experiments(context: dict) -> None:
    protocol = context["protocol"]
    write_json(context["destination"] / "environment.json", {**software_environment(), "torch_cuda_available": torch.cuda.is_available(), "torch_cuda_version": torch.version.cuda, "cudnn_version": torch.backends.cudnn.version(), "protocol_sha256": sha256(context["destination"] / "protocol.json")})
    with threadpool_limits(limits=4):
        for target, assets in protocol["fixed_split"].items():
            for asset in assets:
                windows = load_windows(context["original"] / asset)
                experiment_job(windows, {"asset": asset, "target": target, "design": "fixed_split", "fold": 0}, context)
        for asset in protocol["walk_forward"]["assets"]:
            windows = load_windows(context["original"] / asset)
            for fold, partition in enumerate(walk_forward_partitions(windows, protocol["walk_forward"]["folds"]), 1):
                experiment_job(replace(windows, partitions=partition), {"asset": asset, "target": "price_change", "design": "walk_forward", "fold": fold}, context)


def aggregate_experiments(destination: Path) -> None:
    tables = [pd.read_csv(path) for path in sorted((destination / "experiments").rglob("predictions.csv"))]
    predictions = pd.concat(tables, ignore_index=True)
    predictions.to_csv(destination / "new_predictions.csv", index=False)
    metric_rows = []
    for keys, group in predictions.groupby(["design", "target", "asset", "model"], sort=False):
        assert not group.target_date.duplicated().any()
        group = group.sort_values("target_date")
        metric_rows.append({**dict(zip(["design", "target", "asset", "model"], keys)), **evaluation_metrics(group)})
    pd.DataFrame(metric_rows).to_csv(destination / "new_metrics.csv", index=False)
    write_json(destination / "new_metrics.json", metric_rows)
