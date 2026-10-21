import numpy as np
import pandas as pd
import pytest

from xai_finance.data.features import features
from xai_finance.data.preprocess import fit_training_scalers
from xai_finance.data.split import chronological_indices
from xai_finance.data.validate import validate_prices
from xai_finance.data.windows import build_windows


@pytest.mark.parametrize("frequency", ["daily", "monthly"])
def test_future_price_mutation_preserves_past_features(analytic_prices, frequency):
    prices = analytic_prices if frequency == "daily" else analytic_prices[["close"]]
    cutoff = prices.index[190]
    changed = prices.copy()
    changed.loc[changed.index > cutoff] *= 20
    original = features(prices, frequency)
    mutated = features(changed, frequency)
    pd.testing.assert_frame_equal(original.loc[:cutoff], mutated.loc[:cutoff])


def test_targets_are_exactly_next_observed_close_and_windows_end_at_origin(analytic_prices):
    engineered = features(analytic_prices, "daily")
    windows = build_windows(engineered, 30)
    next_dates = analytic_prices.index[analytic_prices.index.get_indexer(windows.origins) + 1]
    assert windows.targets.equals(next_dates)
    np.testing.assert_array_equal(windows.y, analytic_prices.loc[next_dates, "adj_close"])
    np.testing.assert_array_equal(windows.x[:, -1, 0], analytic_prices.loc[windows.origins, "adj_close"])
    np.testing.assert_array_equal(windows.x[0], engineered.iloc[:30])
    assert (windows.origins < windows.targets).all()


def test_split_targets_never_cross_partition_boundary(window_fixture):
    partitions = window_fixture.partitions
    count = len(window_fixture.y)
    assert len(partitions["train"]) == int(0.8 * count)
    assert len(partitions["validation"]) == int(0.1 * count)
    assert sum(len(indices) for indices in partitions.values()) == count
    for earlier, later in [("train", "validation"), ("validation", "test")]:
        assert window_fixture.targets[partitions[earlier][-1]] < window_fixture.targets[partitions[later][0]]
        assert window_fixture.targets[partitions[earlier][-1]] <= window_fixture.origins[partitions[later][0]]


def test_heldout_mutation_cannot_change_fitted_scalers(window_fixture):
    before = fit_training_scalers(window_fixture)
    validation_and_test = np.r_[window_fixture.partitions["validation"], window_fixture.partitions["test"]]
    window_fixture.x[validation_and_test] *= 1000
    window_fixture.y[validation_and_test] *= 1000
    after = fit_training_scalers(window_fixture)
    np.testing.assert_array_equal(before.inputs.mean_, after.inputs.mean_)
    np.testing.assert_array_equal(before.target.mean_, after.target.mean_)
    assert before.fitted_target_cutoff < str(window_fixture.targets[validation_and_test[0]].date())


def test_target_inverse_transform_restores_original_units(window_fixture):
    scalers = fit_training_scalers(window_fixture)
    normalized = scalers.target.transform(window_fixture.y[:, None])
    np.testing.assert_allclose(scalers.inverse_target(normalized), window_fixture.y, rtol=1e-12)


@pytest.mark.parametrize("fault", ["duplicate", "reversed", "bad_high", "nan"])
def test_invalid_provider_snapshot_is_rejected(analytic_prices, fault):
    if fault == "duplicate":
        analytic_prices = pd.concat([analytic_prices, analytic_prices.iloc[[-1]]])
    elif fault == "reversed":
        analytic_prices = analytic_prices.iloc[::-1]
    elif fault == "bad_high":
        analytic_prices.iloc[0, analytic_prices.columns.get_loc("high")] = 0
    else:
        analytic_prices.iloc[0, 0] = np.nan
    with pytest.raises(ValueError):
        validate_prices(analytic_prices, "daily")


def test_insufficient_history_fails_instead_of_empty_test_set():
    with pytest.raises(ValueError, match="Too few"):
        chronological_indices(5)
