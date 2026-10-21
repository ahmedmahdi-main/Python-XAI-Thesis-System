import numpy as np

from xai_finance.evaluate.metrics import forecast_metrics


def directional_statistics(actual_change: np.ndarray, predicted_change: np.ndarray) -> dict:
    actual_sign, predicted_sign = np.sign(actual_change), np.sign(predicted_change)
    active = predicted_sign != 0
    hits = actual_sign == predicted_sign
    return {"direction_accuracy": float(np.mean(hits)), "direction_coverage": float(np.mean(active)), "direction_accuracy_when_active": float(np.mean(hits[active])) if active.any() else None, "binary_up_accuracy_zero_is_not_up": float(np.mean((actual_change > 0) == (predicted_change > 0))), "actual_up_fraction": float(np.mean(actual_change > 0)), "actual_flat_fraction": float(np.mean(actual_change == 0))}


def paired_bootstrap(actual: np.ndarray, predicted: np.ndarray, zero: np.ndarray) -> dict:
    loss_difference = (predicted - actual) ** 2 - (zero - actual) ** 2
    generator = np.random.default_rng(42)
    block_length, draws = 10, 2000
    starts = generator.integers(0, len(actual), size=(draws, int(np.ceil(len(actual) / block_length))))
    indices = ((starts[..., None] + np.arange(block_length)) % len(actual)).reshape(draws, -1)[:, :len(actual)]
    interval = np.quantile(loss_difference[indices].mean(axis=1), [0.025, 0.975])
    return {"mse_difference_vs_zero": float(np.mean(loss_difference)), "mse_difference_ci_low": float(interval[0]), "mse_difference_ci_high": float(interval[1]), "bootstrap_block_length": block_length, "bootstrap_draws": draws, "bootstrap_seed": 42}


def evaluation_metrics(table) -> dict:
    actual, predicted, current = [table[column].to_numpy() for column in ["actual_price", "predicted_price", "current_price"]]
    metrics = forecast_metrics(actual, predicted, current)
    metrics.update(directional_statistics(actual - current, predicted - current))
    metrics.update(paired_bootstrap(actual, predicted, current))
    metrics["rmse_ratio_vs_zero"] = metrics["rmse"] / float(np.sqrt(np.mean((actual - current) ** 2)))
    target_metrics = forecast_metrics(table.actual_target.to_numpy(), table.predicted_target.to_numpy(), np.zeros(len(table)))
    metrics.update({f"target_{name}": target_metrics[name] for name in ["mae", "rmse", "r2", "mape_percent", "mape_excluded_zero_targets"]})
    return metrics
