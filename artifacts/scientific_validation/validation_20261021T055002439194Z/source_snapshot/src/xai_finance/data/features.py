import numpy as np
import pandas as pd


def relative_strength(close: pd.Series) -> pd.Series:
    changes = close.diff()
    gains = changes.clip(lower=0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    losses = (-changes.clip(upper=0)).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    ratio = gains / losses.replace(0, np.nan)
    rsi = 100 - 100 / (1 + ratio)
    return rsi.mask((losses == 0) & (gains > 0), 100).mask((losses == 0) & (gains == 0), 50)


def features(prices: pd.DataFrame, frequency: str) -> pd.DataFrame:
    close = prices["close"] if frequency == "monthly" else prices["adj_close"]
    engineered = pd.DataFrame({"close": close}, index=prices.index)
    if frequency == "daily":
        adjustment = prices["adj_close"] / prices["close"]
        for column in ["open", "high", "low"]:
            engineered[column] = prices[column] * adjustment
        engineered["log_volume"] = np.log1p(prices["volume"])
    engineered["sma_5"] = close.rolling(5).mean()
    engineered["sma_20"] = close.rolling(20).mean()
    engineered["ema_12"] = close.ewm(span=12, adjust=False, min_periods=12).mean()
    engineered["ema_26"] = close.ewm(span=26, adjust=False, min_periods=26).mean()
    engineered["rsi_14"] = relative_strength(close)
    engineered["macd"] = engineered["ema_12"] - engineered["ema_26"]
    engineered["macd_signal"] = engineered["macd"].ewm(span=9, adjust=False, min_periods=9).mean()
    dispersion = close.rolling(20).std(ddof=0)
    engineered["bollinger_upper"] = engineered["sma_20"] + 2 * dispersion
    engineered["bollinger_lower"] = engineered["sma_20"] - 2 * dispersion
    return return_features(engineered, close).replace([np.inf, -np.inf], np.nan).dropna()


def return_features(engineered: pd.DataFrame, close: pd.Series) -> pd.DataFrame:
    returns = close.pct_change(fill_method=None)
    engineered["return_1"] = returns
    engineered["return_lag_1"] = returns.shift(1)
    engineered["return_lag_5"] = returns.shift(5)
    engineered["volatility_20"] = returns.rolling(20).std(ddof=0)
    engineered["momentum_10"] = close - close.shift(10)
    engineered["trailing_return_20"] = close.pct_change(20, fill_method=None)
    return engineered
