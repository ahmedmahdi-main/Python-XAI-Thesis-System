from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import pandas as pd

from xai_finance.storage import read_json


LEARNED = ["LinearRegression", "RandomForest", "GradientBoosting", "LSTM"]
ASSETS = ["AAPL", "SP500", "NASDAQ", "GOLD", "OIL"]
COLORS = dict(zip(LEARNED + ["Persistence", "Zero"], ["#2c7fb8", "#e69f00", "#a6761d", "#009e73", "#666666", "#666666"]))


def save_figure(figure, destination: Path, name: str) -> None:
    figure.savefig(destination / f"{name}.png", dpi=180, bbox_inches="tight")
    figure.savefig(destination / f"{name}.svg", bbox_inches="tight")
    plt.close(figure)


def frozen_forecasts(original: Path, destination: Path, audits: dict) -> None:
    figure, axes = plt.subplots(3, 2, figsize=(14, 12), constrained_layout=True)
    for axis, asset in zip(axes.ravel(), ASSETS + ["HOUSING"]):
        table = pd.read_csv(original / asset / "predictions.csv", parse_dates=["target_date"])
        actual = table[table.model == "Persistence"]
        axis.plot(actual.target_date, actual.actual, color="black", label="Observed", linewidth=1.5)
        for model in ["RandomForest", "GradientBoosting", "LSTM", "Persistence"]:
            subset = table[table.model == model]
            axis.plot(subset.target_date, subset.predicted, label=model, color=COLORS[model], alpha=0.85, linewidth=1)
        axis.axhline(audits[asset]["shift"]["train_price_max"], color="red", linestyle="--", label="Training maximum")
        axis.set_title(asset)
        axis.set_ylabel(audits[asset]["dataset"]["units"])
        axis.tick_params(axis="x", rotation=25)
    axes[0, 0].legend(fontsize=8)
    figure.suptitle("Frozen level-model forecasts: severe range shift in five series; oil remains in range")
    save_figure(figure, destination, "frozen_level_predictions")


def rmse_comparison(original_metrics, metrics, destination: Path) -> None:
    figure, axes = plt.subplots(1, 3, figsize=(17, 5), constrained_layout=True)
    for axis, target in zip(axes, ["level", "price_change", "simple_return"]):
        if target == "level":
            subset = original_metrics[original_metrics.asset.isin(ASSETS)].copy()
            zero = subset[subset.model == "Persistence"].set_index("asset").rmse
            subset["ratio"] = subset.rmse / subset.asset.map(zero)
        else:
            subset = metrics[(metrics.design == "fixed_split") & (metrics.target == target)].copy()
            subset["ratio"] = subset.rmse_ratio_vs_zero
        assets = [asset for asset in ASSETS if asset in subset.asset.to_list()]
        matrix = subset.pivot(index="asset", columns="model", values="ratio").reindex(index=assets, columns=LEARNED)
        axis.imshow(np.log2(matrix.to_numpy()), cmap="RdBu_r", norm=TwoSlopeNorm(vmin=-0.15, vcenter=0, vmax=5))
        for row in range(len(matrix)):
            for column in range(len(LEARNED)):
                axis.text(column, row, f"{matrix.iloc[row, column]:.3f}", ha="center", va="center", fontsize=9)
        axis.set_xticks(range(4), ["OLS", "RF", "GBM", "LSTM"])
        axis.set_yticks(range(len(assets)), assets)
        axis.set_title(target.replace("_", " "))
    figure.suptitle("Price RMSE / zero-change RMSE; lower is better, 1 = persistence (colors use log2 ratio)")
    save_figure(figure, destination, "target_representation_rmse")


def bootstrap_intervals(metrics, destination: Path) -> None:
    subset = metrics[(metrics.design == "fixed_split") & (metrics.target == "price_change") & metrics.model.isin(LEARNED)]
    figure, axes = plt.subplots(1, 5, figsize=(16, 4), constrained_layout=True)
    for axis, asset in zip(axes, ASSETS):
        selected = subset[subset.asset == asset].set_index("model").reindex(LEARNED)
        baseline_mse = (selected.rmse / selected.rmse_ratio_vs_zero) ** 2
        central = selected.mse_difference_vs_zero / baseline_mse
        low, high = selected.mse_difference_ci_low / baseline_mse, selected.mse_difference_ci_high / baseline_mse
        axis.errorbar(central, range(4), xerr=np.vstack([central - low, high - central]), fmt="o", capsize=3)
        axis.axvline(0, color="black", linestyle="--")
        axis.set_yticks(range(4), ["OLS", "RF", "GBM", "LSTM"])
        axis.set_title(asset)
        axis.set_xlabel("MSE difference / zero MSE")
    figure.suptitle("Price-change models: exploratory paired block-bootstrap 95% intervals; left of zero favors model")
    save_figure(figure, destination, "paired_uncertainty")


def walk_forward_errors(predictions, destination: Path) -> None:
    figure, axes = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)
    for axis, asset in zip(axes, ["AAPL", "SP500"]):
        selected = predictions[(predictions.design == "walk_forward") & (predictions.asset == asset)]
        for model in LEARNED:
            table = selected[selected.model == model].sort_values("target_date")
            delta = (table.predicted_price - table.actual_price) ** 2 - (table.current_price - table.actual_price) ** 2
            axis.plot(pd.to_datetime(table.target_date), delta.cumsum(), label=model, color=COLORS[model])
        for _, fold in selected[selected.model == "Zero"].groupby("fold"):
            axis.axvline(pd.to_datetime(fold.target_date.min()), color="grey", linestyle=":", linewidth=0.8)
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set_title(asset)
        axis.set_ylabel("Cumulative squared-error difference")
        axis.legend(fontsize=8)
    figure.suptitle("Walk-forward price-change forecasts versus zero change; negative favors model; dotted fold starts")
    save_figure(figure, destination, "walk_forward_cumulative_loss")


def directional_accuracy(metrics, destination: Path) -> None:
    subset = metrics[(metrics.design == "fixed_split") & (metrics.target == "price_change")]
    figure, axis = plt.subplots(figsize=(11, 5), constrained_layout=True)
    names = LEARNED + ["TrainMajorityDirectionMedianMagnitude"]
    locations = np.arange(len(ASSETS))
    for offset, name in enumerate(names):
        selected = subset[subset.model == name].set_index("asset").reindex(ASSETS)
        axis.bar(locations + (offset - 2) * 0.15, selected.direction_accuracy, width=0.15, label="Train majority sign" if name == names[-1] else name)
    axis.set_xticks(locations, ASSETS)
    axis.set_ylim(0, 0.75)
    axis.set_ylabel("Three-way sign accuracy")
    axis.legend(fontsize=8, ncol=3)
    axis.set_title("Directional accuracy: zero-change forecast abstains (0% active coverage), omitted from bars")
    save_figure(figure, destination, "directional_accuracy")


def generate_figures(original: Path, destination: Path) -> None:
    output = destination / "figures"
    output.mkdir(exist_ok=True)
    metrics = pd.read_csv(destination / "new_metrics.csv")
    original_metrics = pd.read_csv(destination / "original_metrics_recalculated.csv")
    predictions = pd.read_csv(destination / "new_predictions.csv")
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    frozen_forecasts(original, output, read_json(destination / "original_audit.json"))
    rmse_comparison(original_metrics, metrics, output)
    bootstrap_intervals(metrics, output)
    walk_forward_errors(predictions, output)
    directional_accuracy(metrics, output)
