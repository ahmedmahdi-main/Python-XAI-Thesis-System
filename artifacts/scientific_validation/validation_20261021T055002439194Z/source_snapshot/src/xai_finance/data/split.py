import numpy as np


def chronological_indices(count: int) -> dict[str, np.ndarray]:
    if count < 30:
        raise ValueError("Too few aligned samples for chronological train/validation/test")
    train_end = int(0.8 * count)
    validation_end = train_end + int(0.1 * count)
    return {"train": np.arange(train_end), "validation": np.arange(train_end, validation_end), "test": np.arange(validation_end, count)}
