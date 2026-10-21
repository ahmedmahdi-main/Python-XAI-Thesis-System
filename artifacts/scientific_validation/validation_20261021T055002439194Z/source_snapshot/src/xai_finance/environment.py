import json

import torch

from xai_finance.config import ROOT
from xai_finance.pipelines.train import software_environment
from xai_finance.seed import seed_experiment, select_device
from xai_finance.storage import write_json


def verify_environment() -> None:
    seed_experiment(42)
    device, reason = select_device("auto")
    network = torch.nn.LSTM(8, 16, batch_first=True).to(device)
    output, _ = network(torch.randn(8, 30, 8, device=device))
    output.square().mean().backward()
    if not torch.isfinite(output).all():
        raise FloatingPointError("Hardware LSTM diagnostic nonfinite")
    report = {**software_environment(), "device": str(device), "reason": reason, "torch_cuda": torch.version.cuda, "cuda_available": torch.cuda.is_available(), "lstm_probe_finite": True, "scope": "random tensor hardware diagnostic, not financial results"}
    if device.type == "cuda":
        report["gpu_name"] = torch.cuda.get_device_name(0)
        report["vram_bytes"] = torch.cuda.get_device_properties(0).total_memory
    write_json(ROOT / "artifacts/environment/current.json", report)
    print(json.dumps(report, indent=2))
