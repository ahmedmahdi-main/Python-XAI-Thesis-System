import joblib
import numpy as np
import pytest

from xai_finance.evaluate.metrics import forecast_metrics
from xai_finance.evaluate.regimes import regime_labels
from xai_finance.models.baselines import persistence
from xai_finance.models.sklearn_models import candidates, fit_candidates


def test_metrics_match_hand_computable_original_unit_errors():
    metrics = forecast_metrics(np.array([2, 4]), np.array([1, 5]), np.array([1, 5]))
    assert metrics["mae"] == 1
    assert metrics["rmse"] == 1
    assert metrics["mape_percent"] == 37.5
    assert metrics["r2"] == 0
    assert metrics["direction_accuracy"] == 0


def test_zero_target_mape_is_explicitly_undefined():
    metrics = forecast_metrics(np.zeros(2), np.ones(2), np.zeros(2))
    assert metrics["mape_percent"] is None
    assert metrics["mape_excluded_zero_targets"] == 2
    assert metrics["r2"] is None


def test_persistence_uses_current_close_without_future_labels():
    current = np.array([100, 103, 101])
    np.testing.assert_array_equal(persistence(current), [100, 103, 101])


def test_repeated_forest_inference_is_bitwise_stable(window_fixture):
    """Regression: parallel tree accumulation changed last bits during XAI checks."""
    model, _ = fit_candidates(candidates({"seed": 42, "trees": 40, "search": False})["RandomForest"], window_fixture)
    observations = window_fixture.flat[window_fixture.partitions["test"]]
    expected = model.predict(observations)
    for _ in range(20):
        np.testing.assert_array_equal(expected, model.predict(observations))


def test_regime_boundary_uses_declared_trailing_return_threshold():
    np.testing.assert_array_equal(regime_labels(np.array([0.06, -0.06, 0.05, -0.05, 0]), 0.05), ["bull", "bear", "sideways", "sideways", "sideways"])


@pytest.mark.parametrize("model_name", ["LinearRegression", "RandomForest", "GradientBoosting"])
def test_saved_tabular_model_preserves_predictions_without_refitting(window_fixture, tmp_path, model_name):
    estimators = candidates({"seed": 42, "trees": 5, "search": False})[model_name]
    model, audit = fit_candidates(estimators, window_fixture)
    test = window_fixture.partitions["test"]
    before = model.predict(window_fixture.flat[test])
    joblib.dump(model, tmp_path / "model.joblib")
    reloaded = joblib.load(tmp_path / "model.joblib")
    np.testing.assert_allclose(before, reloaded.predict(window_fixture.flat[test]), atol=1e-8)
    assert audit["trials"][0]["validation_rmse"] >= 0
