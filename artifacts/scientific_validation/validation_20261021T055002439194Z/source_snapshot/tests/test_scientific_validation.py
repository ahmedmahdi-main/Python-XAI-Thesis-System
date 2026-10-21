from dataclasses import replace

import numpy as np
import pytest

from xai_finance.data.preprocess import fit_training_scalers
from xai_finance.validation.design import implied_prices, naive_predictions, target_values, transformed_windows, walk_forward_partitions
from xai_finance.validation.statistics import directional_statistics


@pytest.mark.parametrize("target", ["price_change", "simple_return"])
def test_target_reconstruction_and_scaling_restore_next_price(window_fixture, target):
    transformed = transformed_windows(window_fixture, target)
    scalers = fit_training_scalers(transformed)
    standardized = scalers.target.transform(transformed.y[:, None])
    restored = implied_prices(scalers.inverse_target(standardized), window_fixture.current_close, target)
    np.testing.assert_allclose(restored, window_fixture.y, atol=1e-12)
    assert transformed.x is window_fixture.x
    assert not np.shares_memory(transformed.y, window_fixture.y)


def test_return_protocol_rejects_negative_price_but_changes_preserve_it(window_fixture):
    prices = window_fixture.current_close.copy()
    prices[0] = -1
    altered = replace(window_fixture, current_close=prices)
    with pytest.raises(ValueError, match="strictly positive"):
        target_values(altered, "simple_return")
    np.testing.assert_allclose(implied_prices(target_values(altered, "price_change"), prices, "price_change"), altered.y)


def test_walk_forward_blocks_are_disjoint_and_fit_only_available_labels(window_fixture):
    partitions = walk_forward_partitions(window_fixture, 3)
    np.testing.assert_array_equal(np.concatenate([partition["test"] for partition in partitions]), window_fixture.partitions["test"])
    for partition in partitions:
        assert np.intersect1d(partition["train"], partition["validation"]).size == 0
        assert window_fixture.targets[partition["train"][-1]] <= window_fixture.origins[partition["validation"][0]]
        assert window_fixture.targets[partition["validation"][-1]] <= window_fixture.origins[partition["test"][0]]
    assert len(partitions[-1]["train"]) > len(partitions[0]["train"])


@pytest.mark.parametrize("target", ["price_change", "simple_return"])
def test_naive_predictions_do_not_use_unknown_test_labels(window_fixture, target):
    before = naive_predictions(window_fixture, target)
    test = window_fixture.partitions["test"]
    changed_y = window_fixture.y.copy()
    changed_y[test] *= 2
    altered = replace(window_fixture, y=changed_y)
    after = naive_predictions(altered, target)
    for name in ["Zero", "TrainMean", "TrainMajorityDirectionMedianMagnitude"]:
        np.testing.assert_array_equal(before[name], after[name])
    assert before["LastObservedChangeOrReturn"][0] == after["LastObservedChangeOrReturn"][0]
    np.testing.assert_array_equal(before["LastObservedChangeOrReturn"], target_values(window_fixture, target)[test - 1])


def test_zero_prediction_is_directional_abstention():
    metrics = directional_statistics(np.array([1.0, -1.0, 0.0]), np.zeros(3))
    assert metrics["direction_accuracy"] == pytest.approx(1 / 3)
    assert metrics["direction_coverage"] == 0
    assert metrics["direction_accuracy_when_active"] is None
    assert metrics["binary_up_accuracy_zero_is_not_up"] == pytest.approx(2 / 3)
