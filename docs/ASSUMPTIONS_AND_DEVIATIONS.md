# Assumptions and deviations

CURRENT STATUS: the source became available in the next session and has been fully inspected, including appendix code images. The original missing-source entries below describe the earlier preparation session, not current availability. Verified source hash/anchors and contradictions are in THESIS_TRACEABILITY.md. Authentic data retrieval and actual training now proceed; current results are in per-run artifacts and RECONSTRUCTED_RESULTS.md when generated.

Reconstruction choices: fixed seed 42; daily lookback 30/monthly12; explicit 2015-2025 daily snapshots and 1987-2025 monthly housing; training-only scaling and numerical QR dependence filtering before OLS; one-layer PyTorch LSTM, 32 hidden units, dropout .1, Adam .001, max60 epochs/patience8; small validation-only tree search. Every choice not numerically specified by the narrative is a declared reconstruction default. The appendix's seed42 belongs to its different DecisionTree/XGBoost example, not evidence of an original LSTM configuration.

Source discrepancy: appendix images at P1284/P1285/P1290 reference missing ether.csv, contemporaneous Close, full-data mean filling and an 80/20 split. Narrative/Table4 instead specify four models and 80/10/10. Reconstruction follows the authoritative plan/narrative and never copies this leakage-prone example. No ether.csv contents or survey records have been fabricated.

Execution discrepancies: an initial VRAM probe used eval mode before cuDNN backward; an automated red/green regression confirms the training-mode correction. Initial unfiltered OLS failed SHAP reconstruction due to near-dependent provider-rounded columns; train-only rank filtering corrected numerical conditioning. Superseded diagnostic runs remain preserved, and final experiments are executed fresh. No held-out metric is selected or manually adjusted. FRED's first request used an incorrect graph.csv route; the corrected official fredgraph.csv route successfully returned genuine housing observations.

Data limitation: back-adjusted equity and provider-defined continuous futures snapshots are retrospective, not point-in-time investment datasets. Monthly housing uses revised observation dates without publication vintages; it is a separate retrospective next-observation experiment, not a real-time forecast. Optional macro/sentiment features, walk-forward sensitivity and new human surveys are not claimed.

## Earlier preparation record

Recorded 2026-10-21, user timezone Asia/Baghdad.

- Original thesis unavailable: original-source inspection has not happened. The implementation plan is available and has been read in full. No plan-derived statements are being represented as verified thesis text.
- User explicitly requires PyTorch/CUDA, superseding the original plan's TensorFlow preference. Only LSTM changes backend; the specified sklearn forecasting models remain CPU models.
- Existing project interpreter is CPython 3.12.2, rather than the plan's proposed Python 3.11. Package compatibility and all checks must be verified on the actual interpreter.
- GPU detected through nvidia-smi: RTX 3060 Laptop GPU, 6144 MiB, driver 536.40. Driver-advertised CUDA 12.2 is distinct from the planned PyTorch CUDA 12.1 runtime.
- Pre-install torch import availability check found no installed torch. Therefore torch.cuda.is_available() could not execute before installation; this is recorded as unavailable, not False or passed. Repeat after installing the official compatible wheel.
- PyTorch 2.5.1+cu121 chosen to fit the installed driver, rather than installing an incompatible newer CUDA runtime or changing the machine's driver. Use only trusted project-created checkpoints and explicit weights_only loading where applicable.
- Initial pip request failed because sandbox network sockets were forbidden (WinError 10013), not because the official package was absent. The authorized elevated retry reached the official index and began downloading the CPython 3.12 Windows CUDA wheel.
- Seed 42, lookback 30, small hidden size and bounded epoch budget are proposed reconstruction defaults from the plan/user constraints. They are not claimed to be source-specified or empirically selected.
- No authentic financial snapshot has been retrieved yet. No forecasting model has trained, and no empirical or survey results exist. Random-tensor GPU diagnostics, if executed, are hardware checks only.

- Download diagnostics: the index-selected official download-r2 mirror initially showed no progress. A 1 KiB ranged request to the direct official download.pytorch.org host succeeded (HTTP 206). The initial pip process was interrupted; its partial wheel was approximately 1.5 GiB. A direct-host pip retry is underway. Partial files are not installed distributions and do not establish CUDA availability.

- Final download/install outcome: both full-response attempts were interrupted. The partial official wheel was completed using validated HTTP ranges, then checked against the SHA256 in the official PyTorch index before successful installation. Post-install evidence supersedes the interim status above.
- Verified torch 2.5.1+cu121, CUDA runtime 12.1, cuDNN 90100, CUDA availability True, BF16 support and all eight finite-operation/reload hardware checks. Detailed configuration and results are in artifacts/environment/postinstall.json.
- Fixed-seed random tensors were used only for hardware checks. No asset observations, predictive skill or human trust outcomes were simulated. No research batch size is selected from this probe.
- NumPy is not installed in this bootstrap environment, so torch emitted its optional NumPy-initialization warning; tensor-native hardware checks passed. Install and pin the complete scientific stack only as the next authorized research setup proceeds after source inspection.
