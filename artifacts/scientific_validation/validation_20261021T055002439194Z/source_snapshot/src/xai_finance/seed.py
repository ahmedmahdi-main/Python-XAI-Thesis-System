import os
import random

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np
import torch


def seed_experiment(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.set_num_threads(4)


def select_device(requested: str) -> tuple[torch.device, str]:
    if requested == "cpu":
        return torch.device("cpu"), "CPU explicitly requested"
    if requested not in {"auto", "cuda"}:
        raise ValueError("device must be auto, cuda or cpu")
    if torch.cuda.is_available():
        try:
            torch.ones(1, device="cuda").sum().item()
            return torch.device("cuda"), "CUDA allocation verified"
        except RuntimeError as failure:
            if requested == "cuda":
                raise
            return torch.device("cpu"), f"CUDA runtime failure: {failure}"
    if requested == "cuda":
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is False")
    return torch.device("cpu"), "CUDA unavailable; automatic CPU fallback"
