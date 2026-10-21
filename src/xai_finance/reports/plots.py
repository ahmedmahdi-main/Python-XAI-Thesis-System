from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

PALETTE = ["#22577a", "#b15b24", "#52856e", "#8661a5", "#89939b"]
MODEL_COLORS = dict(zip(["LinearRegression", "RandomForest", "GradientBoosting", "LSTM", "Persistence"], PALETTE))
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10, "figure.dpi": 130, "axes.prop_cycle": plt.cycler(color=PALETTE)})


def save_figure(path: Path, title: str) -> None:
    plt.gcf().suptitle(title, fontsize=10)
    plt.gcf().tight_layout()
    for extension in ["png", "svg"]:
        plt.gcf().savefig(path.with_suffix("." + extension), bbox_inches="tight")
    plt.close("all")


def forecast_charts(predictions: pd.DataFrame, folder: Path, title: str) -> None:
    folder.mkdir(exist_ok=True)
    figure, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    actual = predictions.drop_duplicates("target_date")
    axes[0].plot(pd.to_datetime(actual.target_date), actual.actual, color="#243b53", label="Actual", linewidth=2)
    for model, subset in predictions.groupby("model"):
        axes[0].plot(pd.to_datetime(subset.target_date), subset.predicted, label=model, alpha=0.8, color=MODEL_COLORS[model])
        axes[1].plot(pd.to_datetime(subset.target_date), subset.predicted - subset.actual, label=model, alpha=0.7, color=MODEL_COLORS[model])
    axes[0].legend(ncol=3, fontsize=8)
    axes[0].set_ylabel("Original target units")
    axes[1].set_ylabel("Prediction error")
    axes[1].axhline(0, color="#89939b", linewidth=0.7)
    save_figure(folder / "forecasts", title + " | held-out TEST only")


def metric_charts(metrics: list[dict], folder: Path, title: str) -> None:
    table = pd.DataFrame(metrics)
    figure, axes = plt.subplots(1, 3, figsize=(12, 4))
    for axis, metric in zip(axes, ["mae", "rmse", "r2"]):
        axis.bar(table.model, table[metric], color=[MODEL_COLORS[name] for name in table.model])
        axis.set_title(metric.upper())
        axis.tick_params(axis="x", rotation=65)
    save_figure(folder / "metrics", title)


def loss_chart(history: list[dict], folder: Path) -> None:
    history = pd.DataFrame(history)
    plt.figure(figsize=(8, 4))
    plt.plot(history.epoch, history.train_loss, label="Training")
    plt.plot(history.epoch, history.validation_loss, label="Validation")
    plt.legend()
    plt.xlabel("Epoch")
    plt.ylabel("MSE in training-standardized target units")
    save_figure(folder / "loss", "LSTM training and validation history")


def research_flow(folder: Path) -> None:
    folder.mkdir(exist_ok=True)
    figure, axis = plt.subplots(figsize=(12, 5))
    axis.set_xlim(0, 12)
    axis.set_ylim(0, 5)
    axis.axis("off")
    nodes = [(1, 3, "Authentic history\nfixed snapshot + hash"), (3.4, 3, "Trailing features\nidentical historical windows"), (5.8, 3, "80/10/10 labels\ntrain-only transforms"), (8.2, 3, "Four forecasting models\nvalidation-only selection"), (10.6, 3, "Frozen forecasts\nheld-out TEST dates"), (8.2, 1, "SHAP + LIME\ntraining-only background"), (10.6, 1, "Original-unit metrics\n+ persistence baseline")]
    for x, y, label in nodes:
        axis.text(x, y, label, ha="center", va="center", fontsize=9, bbox={"boxstyle": "round,pad=.6", "facecolor": "#e9eff5", "edgecolor": "#22577a"})
    for start, end in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (4, 6)]:
        axis.annotate("", xy=(nodes[end][0], nodes[end][1] + (0.5 if end > 4 else 0)), xytext=(nodes[start][0] + (0.9 if end < 5 else 0), nodes[start][1]), arrowprops={"arrowstyle": "->", "color": "#22577a"})
    axis.text(6, 0.2, "Post-hoc explanations preserve forecasts. Revised monthly housing is a separate retrospective experiment.", ha="center", fontsize=9)
    save_figure(folder / "research_flow", "Reconstructed research protocol")


def explanation_charts(explanation: shap.Explanation, folder: Path, context: dict) -> None:
    title = context["title"]
    shap.plots.beeswarm(explanation, max_display=12, show=False)
    save_figure(folder / "shap_summary", title + " | fixed declared TEST subset")
    shap.plots.waterfall(explanation[0], max_display=12, show=False)
    save_figure(folder / "shap_waterfall", title + " | local prediction " + context["date"])
    top = int(np.argmax(np.abs(explanation.values).mean(axis=0)))
    plt.figure(figsize=(7, 4))
    plt.scatter(explanation.data[:, top], explanation.values[:, top], color=PALETTE[0])
    plt.xlabel(explanation.feature_names[top])
    plt.ylabel("SHAP contribution (original target units)")
    save_figure(folder / "shap_dependence", title + " | sparse fixed-subset dependence")
    force = shap.force_plot(float(np.asarray(explanation.base_values).ravel()[0]), explanation.values[0], explanation.data[0], feature_names=explanation.feature_names)
    shap.save_html(str(folder / "shap_force.html"), force)
    aggregate_lag_charts(explanation, folder, context)


def aggregate_lag_charts(explanation: shap.Explanation, folder: Path, context: dict) -> None:
    values = explanation.values.reshape(len(explanation.values), context["lookback"], len(context["features"]))
    importance = np.abs(values).sum(axis=1).mean(axis=0)
    ranking = pd.DataFrame({"feature": context["features"], "mean_sum_abs_shap_over_lags": importance}).sort_values("mean_sum_abs_shap_over_lags", ascending=False)
    ranking.to_csv(folder / "global_importance.csv", index=False)
    plt.figure(figsize=(8, 5))
    top = ranking.head(10).iloc[::-1]
    plt.barh(top.feature, top.mean_sum_abs_shap_over_lags, color=PALETTE[0])
    plt.xlabel("Mean sum of absolute SHAP contributions over lags")
    save_figure(folder / "global_importance", context["title"])
    plt.figure(figsize=(10, 6))
    maximum = max(float(np.abs(values[0]).max()), 1e-12)
    plt.imshow(values[0].T, aspect="auto", cmap="RdBu_r", vmin=-maximum, vmax=maximum)
    plt.yticks(range(len(context["features"])), context["features"])
    plt.xlabel("Window position: oldest to newest")
    plt.colorbar(label="Signed SHAP contribution in original target units")
    save_figure(folder / "feature_time_heatmap", context["title"] + " | local " + context["date"])
