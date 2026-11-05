# شرح `tests/test_temporal_integrity.py`

بصمة المصدر SHA-256: `956f8288c073dc7938f6cc1202e9165bab37409a23827cab7fa7b0cf9eea7142`.

وصف الاختبارات لا يعني أنها شُغلت في جلسة التوثيق.

## الأسطر 1–9

```python
import numpy as np
import pandas as pd
import pytest

from xai_finance.data.features import features
from xai_finance.data.preprocess import fit_training_scalers
from xai_finance.data.split import chronological_indices
from xai_finance.data.validate import validate_prices
from xai_finance.data.windows import build_windows
```

يستورد مكتبات الاختبار ودوال السمات والتقييس والتقسيم والتحقق وبناء النوافذ.

## الأسطر 12–20

```python
@pytest.mark.parametrize("frequency", ["daily", "monthly"])
def test_future_price_mutation_preserves_past_features(analytic_prices, frequency):
    prices = analytic_prices if frequency == "daily" else analytic_prices[["close"]]
    cutoff = prices.index[190]
    changed = prices.copy()
    changed.loc[changed.index > cutoff] *= 20
    original = features(prices, frequency)
    mutated = features(changed, frequency)
    pd.testing.assert_frame_equal(original.loc[:cutoff], mutated.loc[:cutoff])
```

يغير الأسعار بعد حد زمني لعينة يومية وشهرية ويتحقق من ثبات السمات السابقة؛ لا يثبت سلامة الإصدارات التاريخية للمزود.

## الأسطر 23–31

```python
def test_targets_are_exactly_next_observed_close_and_windows_end_at_origin(analytic_prices):
    engineered = features(analytic_prices, "daily")
    windows = build_windows(engineered, 30)
    next_dates = analytic_prices.index[analytic_prices.index.get_indexer(windows.origins) + 1]
    assert windows.targets.equals(next_dates)
    np.testing.assert_array_equal(windows.y, analytic_prices.loc[next_dates, "adj_close"])
    np.testing.assert_array_equal(windows.x[:, -1, 0], analytic_prices.loc[windows.origins, "adj_close"])
    np.testing.assert_array_equal(windows.x[0], engineered.iloc[:30])
    assert (windows.origins < windows.targets).all()
```

يتحقق أن الهدف هو الإغلاق المعدل للرصد الخام التالي وأن نهاية كل نافذة عند الأصل، وأن أول نافذة تتطابق مع أول ثلاثين صف سمة.

## الأسطر 34–42

```python
def test_split_targets_never_cross_partition_boundary(window_fixture):
    partitions = window_fixture.partitions
    count = len(window_fixture.y)
    assert len(partitions["train"]) == int(0.8 * count)
    assert len(partitions["validation"]) == int(0.1 * count)
    assert sum(len(indices) for indices in partitions.values()) == count
    for earlier, later in [("train", "validation"), ("validation", "test")]:
        assert window_fixture.targets[partitions[earlier][-1]] < window_fixture.targets[partitions[later][0]]
        assert window_fixture.targets[partitions[earlier][-1]] <= window_fixture.origins[partitions[later][0]]
```

يتحقق من حجم التدريب والتحقق ومجموع الأقسام وترتيب تواريخ الأهداف وإتاحة التسمية السابقة عند أصل القسم التالي.

## الأسطر 45–53

```python
def test_heldout_mutation_cannot_change_fitted_scalers(window_fixture):
    before = fit_training_scalers(window_fixture)
    validation_and_test = np.r_[window_fixture.partitions["validation"], window_fixture.partitions["test"]]
    window_fixture.x[validation_and_test] *= 1000
    window_fixture.y[validation_and_test] *= 1000
    after = fit_training_scalers(window_fixture)
    np.testing.assert_array_equal(before.inputs.mean_, after.inputs.mean_)
    np.testing.assert_array_equal(before.target.mean_, after.target.mean_)
    assert before.fitted_target_cutoff < str(window_fixture.targets[validation_and_test[0]].date())
```

يضرب نوافذ وأهداف التحقق والاختبار في 1000 ثم يعيد ملاءمة المعايير، ويتأكد من ثبات متوسطَي التدريب وسبق آخر هدف تدريب؛ يعدل fixture مؤقتاً.

## الأسطر 56–59

```python
def test_target_inverse_transform_restores_original_units(window_fixture):
    scalers = fit_training_scalers(window_fixture)
    normalized = scalers.target.transform(window_fixture.y[:, None])
    np.testing.assert_allclose(scalers.inverse_target(normalized), window_fixture.y, rtol=1e-12)
```

يتحقق من أن معيار الهدف وعكسه يسترجعان الوحدات الأصلية ضمن rtol محدد.

## الأسطر 62–73

```python
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
```

يحقن تكرار تاريخ أو ترتيباً معكوساً أو high خاطئاً أو NaN ويتوقع ValueError من تحقق الأسعار.

## الأسطر 76–78

```python
def test_insufficient_history_fails_instead_of_empty_test_set():
    with pytest.raises(ValueError, match="Too few"):
        chronological_indices(5)
```

يتوقع رفض تقسيم خمس عينات بدلاً من إنتاج اختبار فارغ.
