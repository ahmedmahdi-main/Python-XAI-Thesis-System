# Reproducing the additive scientific validation

The original experiment, raw snapshots, model checkpoints, thesis, hashes and offline defense package are read-only inputs. The executed addendum is under `artifacts/scientific_validation/validation_20261021T055002439194Z`. Do not execute the original report/package generators to reproduce this review: those generators target the original deliverables.

The existing `.venv` contains the pinned dependencies. No new packages or network downloads were required. The environment is recorded in the addendum's `environment.json`; CUDA 12.1 PyTorch 2.5.1 ran on the 6 GiB RTX 3060 Laptop GPU. Automatic CPU fallback remains available through the original training implementation. CPU numerical training outcomes may differ; exact replication evidence concerns the recorded hardware/software.

To create a **new** independent output directory and a new inventory/protocol, run from the project root in PowerShell:

```powershell
$env:PYTHONHASHSEED = '42'
.\.venv\Scripts\python.exe scripts/start_scientific_validation.py
```

Use the newly printed directory as `$validationFolder` in the following commands. Do not substitute the completed directory when training from scratch. A completed job can be resumed only after its hashes match; an incomplete preexisting job fails rather than overwriting its checkpoints.

```powershell
$validationFolder = 'artifacts/scientific_validation/validation_NEW_TIMESTAMP'
.\.venv\Scripts\python.exe scripts/run_scientific_validation.py $validationFolder audit
.\.venv\Scripts\python.exe scripts/run_scientific_validation.py $validationFolder train
.\.venv\Scripts\python.exe -c "from pathlib import Path; from xai_finance.validation.diagnostics import supplemental_audit; supplemental_audit(Path('artifacts/runs/full_20261021T040901084647Z'), Path('$validationFolder'))"
.\.venv\Scripts\python.exe scripts/replicate_validation_lstm.py $validationFolder
.\.venv\Scripts\python.exe scripts/diagnose_validation_replay.py $validationFolder
.\.venv\Scripts\python.exe -m pytest -q --junitxml="$validationFolder/tests_final.xml" *> "$validationFolder/tests_final.log"
.\.venv\Scripts\python.exe scripts/verify_scientific_validation.py $validationFolder
.\.venv\Scripts\python.exe scripts/audit_reconstruction_precision.py $validationFolder
.\.venv\Scripts\python.exe scripts/build_validation_report.py $validationFolder
```

The report builder writes the report into the new directory and creates `docs/SCIENTIFIC_VALIDATION_REPORT.md` only if that path does not already exist. It leaves a previous canonical report untouched and never changes the original run or original defense package. When reproducing after a prior review, use the report inside the new output directory as the canonical per-run report. The preservation verifier includes previously existing documentation in its inventory. Keep all previous validation directories unchanged.

The protocol deliberately fixes the features, targets, candidates, seeds, splits, epoch caps, walk-forward assets/folds and bootstrap settings. Existing test outcomes were already known before this addendum; the work is exploratory. Running it again does not make the same test period an independent holdout.

Every training job saves `design.json`, `target_and_partitions.npz`, three fitted sklearn models, LSTM scalers and best/last checkpoints, epoch history, candidate/selection metadata, CPU reload checks, predictions, metrics and a SHA256 completion manifest. `new_metrics.csv/json` aggregates only these jobs, with walk-forward test blocks disjoint. `original_metrics_recalculated.csv`, `frozen_level_rmse_separate.csv` and `thesis_reported_separate.csv` retain distinct provenance. Original windows are referenced by immutable path and hash rather than duplicated.

The new fitted models' `predict` methods return **change or return units**, as identified by the companion `design.json`. Reconstruct prices with `xai_finance.validation.design.implied_prices` and the observed origin price; do not display raw target predictions as price forecasts. The original dashboard continues to read the frozen level-model run and does not load this addendum's models.

For exact replay, preserve the model's native output dtype. LSTM predictions are FP32, so `1 + predicted_return` rounds in FP32 before multiplication by the FP64 origin price. The precision audit explicitly casts to FP64 first and writes **separate** sensitivity predictions and metrics. It never overwrites as-executed results. CUDA replay on the recorded GPU is bitwise exact. CPU replay uses an eight-FP32-epsilon absolute bound in training-target-standard-deviation units, with no relative tolerance, to accommodate measured recurrent-operation accumulation differences across devices. The diagnostic script's exact CUDA check requires a CUDA device; the training framework and normal model loading retain automatic CPU fallback.

For offline defense, open the addendum's `offline_validation.html` directly. It embeds all five PNG charts and the full report and needs no network, dashboard server or Python process. PNG/SVG files and Markdown/CSV evidence are separately available. This supplement does not replace the verified original defense ZIP.
