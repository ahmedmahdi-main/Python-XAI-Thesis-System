import numpy as np
import pandas as pd
import pytest

from xai_finance.data.features import features
from xai_finance.data.windows import build_windows


@pytest.fixture
def analytic_prices():
    """Analytic test fixture only; never used by research download/training commands."""
    index = pd.bdate_range("2020-01-01", periods=330)
    close = 100 + np.arange(len(index)) * 0.1 + np.sin(np.arange(len(index)))
    return pd.DataFrame({"open": close - 0.2, "high": close + 1, "low": close - 1, "close": close, "adj_close": close, "volume": 1000 + np.arange(len(index))}, index=index)


@pytest.fixture
def window_fixture(analytic_prices):
    return build_windows(features(analytic_prices, "daily"), 30)
