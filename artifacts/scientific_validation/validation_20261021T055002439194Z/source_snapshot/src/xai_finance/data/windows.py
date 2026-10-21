from dataclasses import dataclass

import numpy as np
import pandas as pd

from xai_finance.data.split import chronological_indices


@dataclass
class WindowDataset:
    x: np.ndarray
    y: np.ndarray
    origins: pd.DatetimeIndex
    targets: pd.DatetimeIndex
    current_close: np.ndarray
    trailing_returns: np.ndarray
    feature_names: list[str]
    partitions: dict[str, np.ndarray]

    @property
    def flat(self) -> np.ndarray:
        return self.x.reshape(len(self.x), -1)

    @property
    def flat_names(self) -> list[str]:
        return [f"lag_{lag}__{name}" for lag in range(self.x.shape[1] - 1, -1, -1) for name in self.feature_names]


def build_windows(engineered: pd.DataFrame, lookback: int) -> WindowDataset:
    if lookback < 1:
        raise ValueError("lookback must be positive")
    # Boundary cases: first origin has exactly lookback rows; final row is context only.
    origins = np.arange(lookback - 1, len(engineered) - 1)
    partitions = chronological_indices(len(origins))
    matrix = engineered.to_numpy(dtype=np.float64)
    windows = np.stack([matrix[position - lookback + 1:position + 1] for position in origins])
    return WindowDataset(windows, engineered.close.iloc[origins + 1].to_numpy(), engineered.index[origins], engineered.index[origins + 1], engineered.close.iloc[origins].to_numpy(), engineered.trailing_return_20.iloc[origins].to_numpy(), list(engineered.columns), partitions)
