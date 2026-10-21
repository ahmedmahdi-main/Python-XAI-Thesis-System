from datetime import datetime, timezone
from pathlib import Path
import shutil

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px

from xai_finance.config import ROOT
from xai_finance.evaluate.metrics import forecast_metrics
from xai_finance.pipelines.train import load_models, load_windows
from xai_finance.reports.plots import forecast_charts, loss_chart, metric_charts, research_flow, save_figure
from xai_finance.storage import read_json, sha256, write_json


def generate_report(folder: Path) -> None:
    metadata = read_json(folder / "run.json")
    research_flow(folder / "plots")
    asset_summaries = []
    for asset in metadata["assets_completed"]:
        asset_summaries.append(asset_report(folder / asset))
    report = {"run_id": metadata["run_id"], "provenance": "NEWLY_COMPUTED", "generated_utc": datetime.now(timezone.utc).isoformat(), "assets": asset_summaries, "limitations": research_limitations()}
    write_json(folder / "summary.json", report)
    write_research_markdown(folder, report)
    metadata["status"] = "REPORT_GENERATED"
    metadata["reproducibility"] = {"requirements_lock_sha256": sha256(ROOT / "requirements-lock.txt"), "code_sha256": {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path) for path in sorted((ROOT / "src").rglob("*.py"))}}
    write_json(folder / "run.json", metadata)
    write_inventory(folder)
    print(f"Generated report: {folder / 'RESULTS.md'}", flush=True)


def asset_report(folder: Path) -> dict:
    audit = read_json(folder / "data_audit.json")
    metrics = read_json(folder / "metrics.json")
    predictions = pd.read_csv(folder / "predictions.csv")
    verify_saved_metrics(predictions, metrics)
    plots = folder / "plots"
    title = f"{folder.name} | {audit['snapshot']['units']}"
    forecast_charts(predictions, plots, title)
    metric_charts(metrics, plots, title)
    loss_chart(read_json(folder / "LSTM/history.json"), plots)
    extra_charts(folder, plots, predictions, audit)
    export_coefficients(folder)
    figure = px.line(predictions, x="target_date", y="predicted", color="model", title=title + " | TEST predictions")
    actual = predictions.drop_duplicates("target_date")
    figure.add_scatter(x=actual.target_date, y=actual.actual, name="Actual", line={"color": "black"})
    figure.write_html(plots / "forecasts.html", include_plotlyjs=True, full_html=True)
    return {"asset": folder.name, "units": audit["snapshot"]["units"], "frequency": audit["snapshot"]["frequency"], "snapshot_sha256": audit["snapshot"]["sha256"], "raw_observations": audit["snapshot"]["rows"], "split": audit["split"], "metrics": metrics, "training": read_json(folder / "training.json"), "explanations_available": all((folder / name / "explanations/quality.json").exists() for name in ["LinearRegression", "RandomForest", "GradientBoosting", "LSTM"])}


def verify_saved_metrics(predictions: pd.DataFrame, saved: list[dict]) -> None:
    for metric_row in saved:
        subset = predictions[predictions.model == metric_row["model"]]
        recomputed = forecast_metrics(subset.actual, subset.predicted, subset.current_close)
        for metric in ["mae", "rmse", "mape_percent", "r2", "direction_accuracy"]:
            if recomputed[metric] is not None:
                np.testing.assert_allclose(recomputed[metric], metric_row[metric], rtol=1e-8, atol=1e-8)


def extra_charts(folder: Path, plots: Path, predictions: pd.DataFrame, audit: dict) -> None:
    regimes = pd.DataFrame(read_json(folder / "regimes.json"))
    pivot = regimes.pivot(index="regime", columns="model", values="mae")
    pivot.plot.bar(figsize=(10, 5))
    plt.ylabel("MAE (original target units)")
    save_figure(plots / "regime_errors", folder.name + " | predeclared trailing-return regimes")
    windows = load_windows(folder)
    plt.figure(figsize=(11, 4))
    for partition, indices in windows.partitions.items():
        plt.plot(windows.targets[indices], windows.y[indices], label=f"{partition}: {len(indices)} labels")
    plt.legend()
    plt.ylabel(audit["snapshot"]["units"])
    save_figure(plots / "temporal_split", folder.name + " | chronological 80/10/10 labels")
    for row in read_json(folder / "metrics.json"):
        plt.figure(figsize=(4, 4))
        confusion = np.asarray(row["up_down_confusion"])
        plt.imshow(confusion, cmap="Blues")
        for (i, j), count in np.ndenumerate(confusion):
            plt.text(j, i, str(count), ha="center", va="center")
        plt.xticks([0, 1], ["Not up", "Up"])
        plt.yticks([0, 1], ["Not up", "Up"])
        plt.xlabel("Predicted change")
        plt.ylabel("Actual change")
        save_figure(plots / f"confusion_{row['model']}", folder.name + " | " + row["model"])


def export_coefficients(folder: Path) -> None:
    models = load_models(folder, "cpu")
    linear = models["LinearRegression"]
    names = load_windows(folder).flat_names
    scaler, selector, regressor = [step[1] for step in linear.steps]
    coefficients = np.zeros(len(names))
    coefficients[selector.retained_] = regressor.coef_ / scaler.scale_[selector.retained_]
    pd.DataFrame({"feature": names, "coefficient_original_input_units": coefficients}).to_csv(folder / "LinearRegression/coefficients.csv", index=False)
    write_json(folder / "LinearRegression/intercept.json", {"original_input_intercept": float(regressor.intercept_ - np.dot(coefficients, scaler.mean_))})
    write_json(folder / "LinearRegression/rank_audit.json", {"relative_qr_tolerance": selector.relative_tolerance, "training_rank": selector.rank_, "retained_columns": selector.retained_.tolist(), "original_columns": len(names), "attribution_caution": "Dependent columns dropped by a training-only numerical basis choice; zero attributed contribution does not mean economically uninformative."})


def research_limitations() -> list[str]:
    return ["Reconstruction, not exact replication: thesis omits instrument/date/sample/units and narrative hyperparameters; appendix implements different models and split.", "Retrospectively adjusted/revised provider snapshots are not point-in-time historical vintages.", "House-price experiment is monthly, retrospective next-observation regression, not publication-time forecasting or daily trading.", "All four models use identical full windows; flattening increases collinearity and dimensionality for tabular models.", "High price-level R2 does not establish trading skill. Compare with persistence and directional accuracy; no transaction-cost backtest or investment-return claim.", "Bounded SHAP subset and permutation budgets are approximate; correlated-feature marginal masking and LIME neighborhoods may be off-manifold. Attributions are not causal.", "Explanation seed stability is a bounded numerical check, not proof of market robustness or human trust.", "Historical survey claims have no participant count/raw responses; no new human study was conducted.", "Seeded deterministic settings improve repeatability; cross-version/hardware bitwise equality is not guaranteed. Runtime batch probing may choose a different batch on another machine.", "Held-out results are descriptive for one fixed chronological split; no claim of universal model superiority or statistical significance."]


def write_research_markdown(folder: Path, summary: dict) -> None:
    lines = [f"# Newly computed results: {summary['run_id']}", "", "Provenance: NEWLY_COMPUTED. Historical Table 4 is separately stored as THESIS_REPORTED_NOT_REPRODUCED. No survey responses were generated.", ""]
    for asset in summary["assets"]:
        test = asset["split"]["test"]
        lines.extend([f"## {asset['asset']}", "", f"Units: {asset['units']}; frequency: {asset['frequency']}; test labels: {test['target_start']} to {test['target_end']} (n={test['n']}).", "", "| Model | MAE | RMSE | MAPE % | R2 | Direction accuracy |", "| --- | ---: | ---: | ---: | ---: | ---: |"])
        for row in asset["metrics"]:
            fields = [f"{row[key]:.6g}" if row[key] is not None else "undefined" for key in ["mae", "rmse", "mape_percent", "r2", "direction_accuracy"]]
            lines.append("| " + row["model"] + " | " + " | ".join(fields) + " |")
        lines.append("")
    lines.extend(["## Scientific limits", ""] + ["- " + limitation for limitation in summary["limitations"]])
    (folder / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    shutil.copy2(folder / "RESULTS.md", ROOT / "docs/RECONSTRUCTED_RESULTS.md")


def write_inventory(folder: Path) -> None:
    entries = {str(path.relative_to(folder)).replace("\\", "/"): sha256(path) for path in sorted(folder.rglob("*")) if path.is_file() and path.name not in {"inventory.json", "verification.json"}}
    write_json(folder / "inventory.json", entries)
