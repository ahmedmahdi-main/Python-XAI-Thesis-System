import numpy as np


def persistence(current_close: np.ndarray) -> np.ndarray:
    return np.asarray(current_close, dtype=float).copy()
