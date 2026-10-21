import numpy as np
from sklearn.metrics import confusion_matrix, mean_absolute_error, mean_squared_error, r2_score


def forecast_metrics(actual: np.ndarray, predicted: np.ndarray, current: np.ndarray) -> dict:
    actual, predicted, current = [np.asarray(series, dtype=float).ravel() for series in (actual, predicted, current)]
    if len(actual) == 0 or actual.shape != predicted.shape or actual.shape != current.shape:
        raise ValueError("Aligned, nonempty actual/predicted/current arrays required")
    if not all(np.isfinite(series).all() for series in (actual, predicted, current)):
        raise ValueError("Metrics require finite values in original units")
    nonzero = np.abs(actual) > 1e-12
    up_true, up_pred = actual > current, predicted > current
    confusion = confusion_matrix(up_true, up_pred, labels=[False, True])
    return {"mae": float(mean_absolute_error(actual, predicted)), "rmse": float(np.sqrt(mean_squared_error(actual, predicted))), "mape_percent": float(np.mean(np.abs((actual[nonzero] - predicted[nonzero]) / actual[nonzero])) * 100) if nonzero.any() else None, "mape_excluded_zero_targets": int((~nonzero).sum()), "r2": float(r2_score(actual, predicted)) if len(actual) > 1 and np.ptp(actual) > 0 else None, "direction_accuracy": float(np.mean(np.sign(predicted - current) == np.sign(actual - current))), "up_down_confusion": confusion.tolist(), "up_precision": float(confusion[1, 1] / confusion[:, 1].sum()) if confusion[:, 1].sum() else None, "up_recall": float(confusion[1, 1] / confusion[1].sum()) if confusion[1].sum() else None, "n": len(actual)}
