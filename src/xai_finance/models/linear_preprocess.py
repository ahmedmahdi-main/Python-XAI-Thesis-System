import numpy as np
from scipy.linalg import qr
from sklearn.base import BaseEstimator, TransformerMixin


class IndependentColumns(TransformerMixin, BaseEstimator):
    """Training-only QR removes dependent coordinates before ordinary least squares."""

    def __init__(self, relative_tolerance: float = 1e-10):
        self.relative_tolerance = relative_tolerance

    def fit(self, inputs: np.ndarray, target=None):
        _, triangular, pivots = qr(inputs, mode="economic", pivoting=True)
        diagonal = np.abs(np.diag(triangular))
        self.rank_ = int((diagonal > diagonal[0] * self.relative_tolerance).sum())
        # A constant-only design still needs one column for sklearn's intercept-only OLS fit.
        self.retained_ = np.sort(pivots[:max(1, self.rank_)])
        self.n_features_in_ = inputs.shape[1]
        return self

    def transform(self, inputs: np.ndarray) -> np.ndarray:
        return np.asarray(inputs)[:, self.retained_]
