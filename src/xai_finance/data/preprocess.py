from dataclasses import dataclass

import numpy as np
from sklearn.preprocessing import StandardScaler

from xai_finance.data.windows import WindowDataset


@dataclass
class TrainingScalers:
    inputs: StandardScaler
    target: StandardScaler
    fitted_origin_cutoff: str
    fitted_target_cutoff: str

    def transform_windows(self, windows: np.ndarray) -> np.ndarray:
        shape = windows.shape
        return self.inputs.transform(windows.reshape(-1, shape[-1])).reshape(shape).astype(np.float32)

    def inverse_target(self, predictions: np.ndarray) -> np.ndarray:
        return self.target.inverse_transform(np.asarray(predictions).reshape(-1, 1)).ravel()


def fit_training_scalers(windows: WindowDataset) -> TrainingScalers:
    training = windows.partitions["train"]
    sequence = windows.x[training]
    scalers = TrainingScalers(StandardScaler().fit(sequence.reshape(-1, sequence.shape[-1])), StandardScaler().fit(windows.y[training, None]), str(windows.origins[training[-1]].date()), str(windows.targets[training[-1]].date()))
    return scalers
