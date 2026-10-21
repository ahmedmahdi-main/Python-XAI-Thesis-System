import numpy as np
import pandas as pd

from xai_finance.evaluate.metrics import forecast_metrics


def regime_labels(trailing_returns: np.ndarray, threshold: float) -> np.ndarray:
    return np.select([trailing_returns > threshold, trailing_returns < -threshold], ["bull", "bear"], default="sideways")


def regime_metrics(predictions: pd.DataFrame) -> list[dict]:
    summaries = []
    for (model, regime), subset in predictions.groupby(["model", "regime"]):
        summaries.append({"model": model, "regime": regime, **forecast_metrics(subset.actual, subset.predicted, subset.current_close)})
    return summaries
