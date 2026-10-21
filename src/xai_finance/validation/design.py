from dataclasses import replace

import numpy as np

from xai_finance.data.windows import WindowDataset


def target_values(windows: WindowDataset, target: str) -> np.ndarray:
    if target == "price_change":
        return windows.y - windows.current_close
    if target == "simple_return":
        if np.any(windows.current_close <= 0) or np.any(windows.y <= 0):
            raise ValueError("Simple-return protocol requires strictly positive prices")
        return windows.y / windows.current_close - 1
    raise ValueError(f"Unknown target: {target}")


def implied_prices(predicted: np.ndarray, current: np.ndarray, target: str) -> np.ndarray:
    if target == "price_change":
        return current + predicted
    if target == "simple_return":
        return current * (1 + predicted)
    raise ValueError(f"Unknown target: {target}")


def transformed_windows(windows: WindowDataset, target: str) -> WindowDataset:
    return replace(windows, y=target_values(windows, target))


def walk_forward_partitions(windows: WindowDataset, folds: int) -> list[dict]:
    validation_size = len(windows.partitions["validation"])
    partitions = []
    for test in np.array_split(windows.partitions["test"], folds):
        cutoff = int(test[0])
        training_end = cutoff - validation_size
        if training_end < 30:
            raise ValueError("Insufficient pre-fold training history")
        partition = {"train": np.arange(training_end), "validation": np.arange(training_end, cutoff), "test": test}
        assert windows.targets[partition["validation"][-1]] <= windows.origins[test[0]]
        partitions.append(partition)
    return partitions


def naive_predictions(windows: WindowDataset, target: str) -> dict[str, np.ndarray]:
    transformed = target_values(windows, target)
    training = transformed[windows.partitions["train"]]
    test = windows.partitions["test"]
    majority = 1 if np.sum(training > 0) >= np.sum(training < 0) else -1
    nonzero = np.abs(training[training != 0])
    magnitude = float(np.median(nonzero)) if len(nonzero) else 0.0
    if np.any(test < 1):
        raise ValueError("Last-observed baseline requires a prior known target")
    assert (windows.targets[test - 1] <= windows.origins[test]).all()
    return {"Zero": np.zeros(len(test)), "TrainMean": np.full(len(test), np.mean(training)), "LastObservedChangeOrReturn": transformed[test - 1], "TrainMajorityDirectionMedianMagnitude": np.full(len(test), majority * magnitude)}
