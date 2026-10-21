# Verified GPU bootstrap

Date: 2026-10-21. Existing project virtual environment, Python 3.12.2, Windows 11.

| Item | Executed observation |
| --- | --- |
| GPU | NVIDIA GeForce RTX 3060 Laptop GPU |
| VRAM | nvidia-smi: 6144 MiB |
| Driver | 536.40 |
| Driver-advertised CUDA | 12.2; not the installed PyTorch runtime |
| PyTorch | 2.5.1+cu121 |
| PyTorch CUDA runtime | 12.1 |
| cuDNN | 90100 |
| torch.cuda.is_available() | True |
| AMP hardware diagnostic | BF16 LSTM forward/backward and finite gradients passed |
| CPU/CUDA reload agreement | Maximum absolute error 2.9802322387695312e-08 |
| Hardware assertions | 8 passed, diagnostic process exit 0 |
| Preparation assertions | 9 passed |
| pip check | No broken requirements, exit 0 |

The official wheel hash was checked before installation. Full-response transfers stalled; bounded HTTP range requests completed the download. Integrity and environment evidence are in artifacts/environment/pytorch_wheel.json, preinstall.json and postinstall.json. bootstrap-freeze.txt captures the project interpreter's installed packages; it is not a full research lock.

The standard official bootstrap command is:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-gpu.txt
```

Executed diagnostic settings: seed 42; deterministic PyTorch algorithms; CUBLAS_WORKSPACE_CONFIG=:4096:8 before importing torch; cuDNN benchmark and TF32 disabled. Fixture: random inputs shaped (32, 30, 16), LSTM hidden size 32, linear output, Adam and MSE. CPU and CUDA FP32 paths and a CUDA BF16 autocast path were exercised. State serialization/reload was checked in memory with weights_only=True. No financial model checkpoint was created.

The hardware fixture cannot determine predictive performance, the optimal financial training batch, cross-machine bitwise reproducibility or AMP accuracy on the research dataset. NumPy and the complete research stack remain to be installed. Original-thesis inspection is still required before research implementation.

Compatibility references: [official PyTorch previous versions](https://pytorch.org/get-started/previous-versions/), [NVIDIA CUDA 12.1 driver requirements](https://docs.nvidia.com/cuda/archive/12.1.0/cuda-toolkit-release-notes/).
