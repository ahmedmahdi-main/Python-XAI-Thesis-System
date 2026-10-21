import numpy as np
import pytest

from xai_finance.data.features import features
from xai_finance.data.windows import build_windows
from xai_finance.explain.shap_explain import explain_shap, shap_reconstruction
from xai_finance.io.data_sources import load_snapshot
from xai_finance.models.sklearn_models import candidates, fit_candidates


@pytest.mark.integration
def test_real_provider_ols_explanation_reconstructs_stably():
    """Regression: provider-rounded dependent features caused catastrophic OLS cancellation."""
    prices, _ = load_snapshot("AAPL")
    windows = build_windows(features(prices, "daily"), 30)
    model, _ = fit_candidates(candidates({"seed": 42, "trees": 5, "search": False})["LinearRegression"], windows)
    indices = windows.partitions["test"][np.linspace(0, len(windows.partitions["test"]) - 1, 10, dtype=int)]
    background = windows.flat[windows.partitions["train"][np.linspace(0, len(windows.partitions["train"]) - 1, 8, dtype=int)]]
    request = {"observations": windows.flat[indices], "names": windows.flat_names, "seed": 42, "cycles": 1}
    explanation = explain_shap("LinearRegression", model, background, request)
    audit = shap_reconstruction(explanation, model.predict(windows.flat[indices]))
    assert audit["max_absolute_error"] < 1e-3
