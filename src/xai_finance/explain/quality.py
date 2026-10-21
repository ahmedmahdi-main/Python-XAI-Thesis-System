import numpy as np
from scipy.stats import spearmanr


def attribution_stability(first: np.ndarray, second: np.ndarray) -> dict:
    first, second = np.abs(first), np.abs(second)
    count = min(10, len(first))
    overlap = len(set(np.argsort(first)[-count:]) & set(np.argsort(second)[-count:])) / count
    correlation = spearmanr(first, second).statistic if np.ptp(first) and np.ptp(second) else None
    return {"top_10_overlap": overlap, "spearman_abs_attribution_rank": float(correlation) if correlation is not None and np.isfinite(correlation) else None, "scope": "Same observation rerun with a different explainer seed; not human trust or robustness to all market shifts"}


def lime_weight_vector(explanation, count: int) -> np.ndarray:
    weights = np.zeros(count)
    for feature, weight in explanation.as_map()[1]:
        weights[feature] = weight
    return weights
