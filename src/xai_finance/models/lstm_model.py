from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np
import torch
from torch import nn

from xai_finance.data.preprocess import TrainingScalers, fit_training_scalers
from xai_finance.data.windows import WindowDataset
from xai_finance.seed import select_device
from xai_finance.storage import write_json


class PriceLSTM(nn.Module):
    def __init__(self, architecture: dict):
        super().__init__()
        self.lstm = nn.LSTM(architecture["features"], architecture["hidden_size"], batch_first=True)
        self.dropout = nn.Dropout(architecture["dropout"])
        self.output = nn.Linear(architecture["hidden_size"], 1)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        sequence, _ = self.lstm(inputs)
        return self.output(self.dropout(sequence[:, -1, :])).squeeze(-1)


@dataclass
class LSTMPredictor:
    network: PriceLSTM
    scalers: TrainingScalers
    lookback: int
    feature_count: int
    device: torch.device

    def predict(self, flattened: np.ndarray) -> np.ndarray:
        windows = np.asarray(flattened).reshape(-1, self.lookback, self.feature_count)
        scaled = self.scalers.transform_windows(windows)
        self.network.eval()
        outputs = []
        with torch.no_grad():
            for start in range(0, len(scaled), 256):
                batch = torch.as_tensor(scaled[start:start + 256], device=self.device)
                outputs.append(self.network(batch).float().cpu().numpy())
        return self.scalers.inverse_target(np.concatenate(outputs))


def probe_precision(network: PriceLSTM, fixture: tuple, requested: bool) -> tuple[torch.dtype | None, dict]:
    inputs, target = fixture
    if not requested or inputs.device.type != "cuda":
        return None, {"effective_precision": "fp32", "reason": "CPU or AMP disabled"}
    network.eval()
    precision = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    try:
        with torch.no_grad():
            full_loss = nn.functional.mse_loss(network(inputs), target)
            with torch.autocast("cuda", dtype=precision):
                mixed = network(inputs)
            mixed_loss = nn.functional.mse_loss(mixed.float(), target)
        difference = float(abs(mixed_loss - full_loss) / full_loss.clamp_min(1e-8))
        if not torch.isfinite(mixed_loss) or difference > 0.05:
            return None, {"effective_precision": "fp32", "reason": "AMP training-fixture loss differs by >5% or is nonfinite", "relative_loss_difference": difference if np.isfinite(difference) else None}
        return precision, {"effective_precision": str(precision), "relative_loss_difference": difference, "criterion": "finite training-fixture loss within 5% of FP32"}
    except RuntimeError as failure:
        return None, {"effective_precision": "fp32", "reason": str(failure)}


def scaled_loss(network: PriceLSTM, fixture: tuple, precision: torch.dtype | None) -> torch.Tensor:
    inputs, target = fixture
    with torch.autocast(device_type=inputs.device.type, dtype=precision, enabled=precision is not None):
        predictions = network(inputs)
    return nn.functional.mse_loss(predictions.float(), target)


def batch_probe(network: PriceLSTM, fixture: tuple, configuration: dict) -> tuple[int, list[dict]]:
    inputs, target = fixture
    device = inputs.device
    if device.type == "cpu":
        return min(32, len(inputs)), [{"batch_size": min(32, len(inputs)), "reason": "bounded CPU default"}]
    measurements = []
    free_bytes, _ = torch.cuda.mem_get_info()
    for candidate in configuration["batch_candidates"]:
        candidate = min(candidate, len(inputs))
        try:
            measurements.append(measure_batch(network, (inputs[:candidate], target[:candidate]), free_bytes))
        except torch.cuda.OutOfMemoryError:
            network.zero_grad(set_to_none=True)
            torch.cuda.empty_cache()
            measurements.append({"batch_size": candidate, "oom": True})
    valid = [measurement for measurement in measurements if measurement.get("accepted")]
    if not valid:
        if min(configuration["batch_candidates"]) <= 1:
            raise RuntimeError("No LSTM batch fits the available VRAM")
        smaller = {**configuration, "batch_candidates": [max(1, min(configuration["batch_candidates"]) // 2)]}
        selected, retries = batch_probe(network, fixture, smaller)
        return selected, measurements + retries
    return max(measurement["batch_size"] for measurement in valid), measurements


def measure_batch(network: PriceLSTM, fixture: tuple, free_bytes: int) -> dict:
    torch.cuda.reset_peak_memory_stats()
    network.train()
    for _ in range(2):
        network.zero_grad(set_to_none=True)
        scaled_loss(network, fixture, None).backward()
    torch.cuda.synchronize()
    started = perf_counter()
    for _ in range(3):
        network.zero_grad(set_to_none=True)
        scaled_loss(network, fixture, None).backward()
    torch.cuda.synchronize()
    elapsed = perf_counter() - started
    peak = torch.cuda.max_memory_allocated()
    return {"batch_size": len(fixture[0]), "samples_per_second": 3 * len(fixture[0]) / elapsed, "elapsed_seconds": elapsed, "peak_allocated_bytes": peak, "free_vram_before_probe": free_bytes, "accepted": peak < 0.8 * free_bytes}


def train_epoch(network: PriceLSTM, tensors: tuple, optimization: dict) -> float:
    inputs, target = tensors
    network.train()
    losses = []
    for start in range(0, len(inputs), optimization["batch_size"]):
        stop = start + optimization["batch_size"]
        optimization["optimizer"].zero_grad(set_to_none=True)
        loss = scaled_loss(network, (inputs[start:stop], target[start:stop]), optimization["precision"])
        if not torch.isfinite(loss):
            raise FloatingPointError("Nonfinite LSTM training loss; run aborted")
        optimization["grad_scaler"].scale(loss).backward()
        optimization["grad_scaler"].unscale_(optimization["optimizer"])
        nn.utils.clip_grad_norm_(network.parameters(), 1.0, error_if_nonfinite=True)
        optimization["grad_scaler"].step(optimization["optimizer"])
        optimization["grad_scaler"].update()
        losses.append((float(loss.detach()), len(inputs[start:stop])))
    return sum(loss * count for loss, count in losses) / len(inputs)


def checkpoint_state(network: PriceLSTM, optimization: dict, progress: dict) -> dict:
    return {"state_dict": network.state_dict(), "optimizer_state": optimization["optimizer"].state_dict(), "amp_scaler_state": optimization["grad_scaler"].state_dict(), "torch_rng_state": torch.get_rng_state(), "cuda_rng_states": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [], **progress}


def optimize_epochs(network: PriceLSTM, tensors: dict, settings: dict) -> tuple[list[dict], dict]:
    optimization, configuration, folder = settings["optimization"], settings["configuration"], settings["folder"]
    best_loss, stale, history, best_state = float("inf"), 0, [], None
    started = perf_counter()
    for epoch in range(configuration["epochs"]):
        training_loss = train_epoch(network, tensors["train"], optimization)
        network.eval()
        with torch.no_grad():
            validation_loss = float(scaled_loss(network, tensors["validation"], None))
        if not np.isfinite(validation_loss):
            raise FloatingPointError("Nonfinite validation loss")
        history.append({"epoch": epoch + 1, "train_loss": training_loss, "validation_loss": validation_loss, "elapsed_seconds": perf_counter() - started})
        progress = {"epoch": epoch + 1, "architecture": settings["architecture"], "configuration": configuration}
        torch.save(checkpoint_state(network, optimization, progress), folder / "last.pt")
        if validation_loss < best_loss:
            best_loss, stale, best_state = validation_loss, 0, deepcopy(network.state_dict())
            torch.save(checkpoint_state(network, optimization, progress), folder / "best.pt")
        else:
            stale += 1
        write_json(folder / "history.json", history)
        print(f"LSTM epoch {epoch + 1}: train={training_loss:.6g}, val={validation_loss:.6g}", flush=True)
        if stale >= configuration["patience"]:
            break
    network.load_state_dict(best_state)
    return history, {"best_validation_scaled_mse": best_loss, "best_epoch": min(history, key=lambda row: row["validation_loss"])["epoch"], "epochs_executed": len(history)}


def fit_lstm(windows: WindowDataset, configuration: dict, folder: Path) -> tuple[LSTMPredictor, dict]:
    started = perf_counter()
    folder.mkdir(parents=True, exist_ok=True)
    device, reason = select_device(configuration["device"])
    scalers = fit_training_scalers(windows)
    tensors = training_tensors(windows, scalers, device)
    architecture = {"features": windows.x.shape[-1], "hidden_size": configuration["hidden_size"], "dropout": configuration["dropout"]}
    network = PriceLSTM(architecture).to(device)
    fixture = tuple(tensor[:max(configuration["batch_candidates"])] for tensor in tensors["train"])
    cpu_rng, cuda_rng = torch.get_rng_state(), torch.cuda.get_rng_state_all() if device.type == "cuda" else []
    precision, precision_audit = probe_precision(network, fixture, configuration["amp"])
    batch_size, probes = batch_probe(network, fixture, configuration)
    torch.set_rng_state(cpu_rng)
    if cuda_rng:
        torch.cuda.set_rng_state_all(cuda_rng)
    optimization = {"batch_size": batch_size, "optimizer": torch.optim.Adam(network.parameters(), lr=configuration["learning_rate"]), "precision": precision, "grad_scaler": torch.amp.GradScaler(device.type, enabled=precision == torch.float16)}
    _, selection = optimize_epochs(network, tensors, {"optimization": optimization, "configuration": configuration, "folder": folder, "architecture": architecture})
    predictor = LSTMPredictor(network, scalers, windows.x.shape[1], windows.x.shape[2], device)
    metadata = {"device": str(device), "device_reason": reason, "precision": precision_audit, "batch_size": batch_size, "batch_probes": probes, "selection": selection, "training_seconds": perf_counter() - started, "scaler_origin_cutoff": scalers.fitted_origin_cutoff, "scaler_target_cutoff": scalers.fitted_target_cutoff}
    return predictor, metadata


def training_tensors(windows: WindowDataset, scalers: TrainingScalers, device: torch.device) -> dict:
    tensors = {}
    for partition in ["train", "validation"]:
        indices = windows.partitions[partition]
        inputs = scalers.transform_windows(windows.x[indices])
        target = scalers.target.transform(windows.y[indices, None]).ravel().astype(np.float32)
        tensors[partition] = (torch.as_tensor(inputs, device=device), torch.as_tensor(target, device=device))
    return tensors


def load_lstm(folder: Path, scalers: TrainingScalers, requested: str = "auto") -> LSTMPredictor:
    device, _ = select_device(requested)
    checkpoint = torch.load(folder / "best.pt", map_location=device, weights_only=True)
    network = PriceLSTM(checkpoint["architecture"]).to(device)
    network.load_state_dict(checkpoint["state_dict"])
    network.eval()
    return LSTMPredictor(network, scalers, checkpoint["configuration"]["effective_lookback"], checkpoint["architecture"]["features"], device)
