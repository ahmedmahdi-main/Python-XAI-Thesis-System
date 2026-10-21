import numpy as np
import pandas as pd


def validate_prices(prices: pd.DataFrame, frequency: str) -> pd.DataFrame:
    required = ["close"] if frequency == "monthly" else ["open", "high", "low", "close", "adj_close", "volume"]
    if not set(required).issubset(prices.columns):
        raise ValueError(f"Missing required columns: {set(required) - set(prices.columns)}")
    if not isinstance(prices.index, pd.DatetimeIndex) or prices.index.hasnans:
        raise ValueError("A non-null DatetimeIndex is required")
    if not prices.index.is_monotonic_increasing or prices.index.has_duplicates:
        raise ValueError("Dates must be unique and strictly chronological")
    if not np.isfinite(prices[required].to_numpy(dtype=float)).all():
        raise ValueError("Unresolved missing or infinite observations")
    if frequency == "daily":
        validate_ohlc(prices)
    if len(prices) < 100:
        raise ValueError("At least 100 genuine observations required")
    return prices


def validate_ohlc(prices: pd.DataFrame) -> None:
    high_ok = prices["high"] + 1e-6 >= prices[["open", "close", "low"]].max(axis=1)
    low_ok = prices["low"] - 1e-6 <= prices[["open", "close", "high"]].min(axis=1)
    if not (high_ok & low_ok).all():
        raise ValueError("OHLC ordering is inconsistent")
    if (prices["volume"] < 0).any() or (prices["close"] == 0).any():
        raise ValueError("Negative volume or zero close cannot be processed")
