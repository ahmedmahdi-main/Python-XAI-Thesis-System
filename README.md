# Saleh financial XAI research system

Executable reconstruction of Mohammad Saleh's master's thesis, *Developing an Explainable Artificial Intelligence (XAI) Framework for Trend Prediction and Analysis in the Stock Market*. Python 3.12.2, Windows, CUDA-enabled PyTorch LSTM plus sklearn LinearRegression/RandomForest/GradientBoosting, SHAP, LIME and a local Streamlit dashboard.

This is newly computed research, not an exact reproduction of historical Table 4. Original data/units/configuration are absent from that table, and appendix screenshots implement different models. Read [verified source traceability](docs/THESIS_TRACEABILITY.md), [methodology](docs/METHODOLOGY.md), [scientific discrepancies](docs/ASSUMPTIONS_AND_DEVIATIONS.md) and [proposed thesis corrections](docs/PROPOSED_THESIS_AMENDMENT.md). No survey records are generated.

## View the saved defense demonstration

From this project directory, with its existing environment:

```powershell
.\.venv\Scripts\python.exe scripts/launch_demo.py
```

Open http://127.0.0.1:8501. Viewing reads local artifacts and requires no live data download, model retraining or external fonts. Select an asset/model and one of the precomputed explanation dates. Both SHAP and LIME identify the same held-out observation. Revised monthly housing has an explicit retrospective limitation.

The portable defense_package directory includes source, datasets, models, reports, charts, original thesis, tests and pinned Windows CPython 3.12 wheels. With Python 3.12 installed, run from that folder:

```powershell
python scripts/offline_demo.py
```

The first run creates a local venv and installs exclusively with --no-index from wheelhouse. Later runs launch directly. The Python installer and a second physical backup medium are not bundled. Do not copy Yahoo session/cookie caches; they are excluded from the package.

## Install and reproduce

Online bootstrap if an environment does not yet exist:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-gpu.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation .
```

The installed driver 536.40 is used with torch 2.5.1+cu121; newer CUDA wheels must not be substituted blindly. CPU fallback is automatic with device=auto; set device=cpu explicitly in a copied YAML to force CPU. A forced unavailable CUDA device fails clearly.

```powershell
$env:PYTHONHASHSEED='42'
python -m xai_finance.cli doctor
python -m xai_finance.cli download --config configs/full_experiment.yaml
python -m xai_finance.cli validate --config configs/full_experiment.yaml
python -m pytest -q
python -m xai_finance.cli train --config configs/full_experiment.yaml
python -m xai_finance.cli explain --config configs/full_experiment.yaml
python -m xai_finance.cli evaluate --config configs/full_experiment.yaml
python -m xai_finance.cli report --config configs/full_experiment.yaml
```

Single-command workflows: `python scripts/run_quick.py` or `python scripts/run_full.py`. Quick uses two core assets, one tree configuration, <=8 LSTM epochs and bounded explanations; full uses five daily assets and one separate monthly index, validation-only tree selection, <=60 epochs and 10 explanation observations per model. The scripts set process-start seeds. No extensive hyperparameter search is performed.

Use the activated project environment or its explicit python.exe for the unqualified commands above. Existing raw snapshots are hash-verified and reused; downloading never silently replaces them. A new snapshot requires an explicitly separate research directory/run protocol. Training creates a timestamped immutable run and does not overwrite historical runs. Failed numerical-diagnostic runs are retained and marked superseded, excluded from default dashboard selection and the defense package.

## Output and evidence

- `data/raw/*.csv`, `data/manifests/*.json`: authentic Yahoo/FRED snapshots and provenance.
- `artifacts/latest_full.json`: current full-run pointer.
- `artifacts/runs/<run_id>/<asset>/`: aligned windows, split audit, saved models, training selection/timing, best/last LSTM checkpoints, loss history, per-model predictions and original-unit metrics, CPU reload checks, regimes and unverified next-snapshot forecast.
- `<asset>/<model>/explanations/`: SHAP NPZ, fidelity/seed stability/overhead JSON, global ranking, summary/waterfall/dependence/force/feature-time charts; LIME JSON/HTML for each precomputed date and a first-date PNG/SVG.
- `<asset>/plots/`: split, actual/predicted, errors, separate-metric bars, confusion matrices, regimes, training curves; PNG/SVG and standalone offline forecast HTML.
- `<run_id>/RESULTS.md`, `summary.json`, `inventory.json`: computed report and artifact hashes.
- `docs/thesis_reported_reference.json`: historical values only, labeled THESIS_REPORTED_NOT_REPRODUCED.
- `artifacts/tests/`: actual JUnit/test/offline-rehearsal evidence; `docs/RESULTS_AUDIT.md`: claim provenance.

Run `python scripts/verify_artifacts.py` to independently recompute metrics and validate artifact hashes, alignment, training cutoffs, saved predictions and explanation conservation. Run `python scripts/offline_smoke.py` to exercise all dashboard datasets/models with external Python socket connections blocked. Generate the portable folder and CRC-verified backup with `python scripts/generate_defense_package.py` after final checks.

Scientific limits: retrospective adjustments/revisions; one fixed test split; no trading-cost/profitability backtest; sparse bounded explanation subsets; correlated-feature masking; no new human trust study. Poor or negative R2 and persistence wins are retained. Diagnostic fixes address demonstrated numerical errors, never tuning against the thesis's scores. See the complete defense script and committee Q&A in docs/.
