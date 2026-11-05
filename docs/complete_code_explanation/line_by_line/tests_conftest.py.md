# شرح `tests/conftest.py`

بصمة المصدر SHA-256: `41ee4b27c2f77914a6efc6a25cb5452bd277dcd104e953578b05f7d9e9cf6b08`.

وصف الاختبارات لا يعني أنها شُغلت في جلسة التوثيق.

## الأسطر 1–6

```python
import numpy as np
import pandas as pd
import pytest

from xai_finance.data.features import features
from xai_finance.data.windows import build_windows
```

يستورد NumPy وpandas وpytest ودالتي السمات والنوافذ لتجهيز اختبارات، لا بيانات بحثية.

## الأسطر 9–14

```python
@pytest.fixture
def analytic_prices():
    """Analytic test fixture only; never used by research download/training commands."""
    index = pd.bdate_range("2020-01-01", periods=330)
    close = 100 + np.arange(len(index)) * 0.1 + np.sin(np.arange(len(index)))
    return pd.DataFrame({"open": close - 0.2, "high": close + 1, "low": close - 1, "close": close, "adj_close": close, "volume": 1000 + np.arange(len(index))}, index=index)
```

fixture ‏analytic_prices ينشئ 330 تاريخ عمل وسعرًا تحليلياً 100+0.1t+sin(t)، وOHLC وحجماً صناعياً؛ يعيد DataFrame للاختبارات فقط.

## الأسطر 17–19

```python
@pytest.fixture
def window_fixture(analytic_prices):
    return build_windows(features(analytic_prices, "daily"), 30)
```

fixture ‏window_fixture يحول الأسعار الصناعية إلى سمات يومية ونوافذ 30 رصداً ويعيدها للاختبارات التابعة.
