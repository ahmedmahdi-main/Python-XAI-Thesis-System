# Saleh financial XAI research system

Executable reconstruction of Mohammad Saleh's master's thesis, *Developing an Explainable Artificial Intelligence (XAI) Framework for Trend Prediction and Analysis in the Stock Market*. Windows x64, Python 3.12, PyTorch LSTM plus sklearn LinearRegression/RandomForest/GradientBoosting, SHAP, LIME and the original eight-tab local Streamlit dashboard. The defense installation uses PyTorch 2.5.1+cpu. Original CUDA research configurations and requirements are preserved.

This is newly computed research, not an exact reproduction of historical Table 4. Original data/units/configuration are absent from that table, and appendix screenshots implement different models. Read [verified source traceability](docs/THESIS_TRACEABILITY.md), [methodology](docs/METHODOLOGY.md), [scientific discrepancies](docs/ASSUMPTIONS_AND_DEVIATIONS.md) and [proposed thesis corrections](docs/PROPOSED_THESIS_AMENDMENT.md). No survey records are generated.

## CPU installation and launch for Mohammad

1. Install **Windows x64 Python 3.12** for your user if it is absent. Python 3.12.13 was tested. The Python installer is not bundled; obtain it before going offline.
2. Copy `Mohammad_XAI_Defense_CPU.zip` and its `.sha256` file to the computer. Verify the ZIP with `Get-FileHash .\Mohammad_XAI_Defense_CPU.zip -Algorithm SHA256` and compare it with the companion file.
3. Extract the **entire ZIP** to a writable local folder, for example `C:\XAI-Defense`. Do not run files inside the ZIP or copy a virtual environment from another computer.
4. Double-click **SETUP_DEMO.bat**. The complete defense ZIP includes `wheelhouse-cpu`: setup installs exclusively from these Windows CPU wheels, without internet, administrator privileges, CUDA, PyCharm or Visual Studio. A source checkout without the wheels requires internet for its first setup.
5. Double-click **START_DEMO.bat**. The launcher opens the browser automatically. It reuses this folder's running server, or chooses a free port from 8501 through 8520 without stopping other services.

Setup creates a new `.demo_venv`; the original research `.venv` is preserved. Setup checks hashes, imports, all saved full-run CPU models and explanations, scientific validation replay, actual dashboard rendering and server health. Installation can take several minutes while native wheels are extracted. Logs and server status are under `.demo_runtime`. Repeat setup safely to repair missing dependencies.

To explicitly require an offline installation, or launch without opening a browser:

```powershell
.\SETUP_DEMO.bat --offline
.\START_DEMO.bat --no-browser
# Stop only this folder's tracked demo server:
.\START_DEMO.bat stop
```

Use the local URL printed by the launcher, normally http://127.0.0.1:8501. Viewing reads local artifacts and requires no live data download, model retraining or external fonts. Forecasts and explanations are explicitly **saved experiment replay**, not current market inference. Select an asset/model and a precomputed explanation date. Both SHAP and LIME identify the same held-out observation. Revised monthly housing has an explicit retrospective limitation. Open Reproducibility → Saved scientific validation results to view the preserved evaluation metrics and download its standalone offline HTML report.

The stable Streamlit entry point is `main.py`, which delegates to the original `dashboard/app.py`. With a working environment, the direct command is:

```powershell
.\.demo_venv\Scripts\python.exe -m streamlit run main.py
```

The package includes all local saved research runs, the protected scientific validation, raw datasets/manifests, explanation artifacts, reports, source and CPU wheels, with SHA-256 integrity hashes. GPU wheels, virtual environments, provider cookie caches and browser profiles are excluded. See [CPU deployment report](docs/CPU_DEPLOYMENT_REPORT.md) and [offline defense instructions](docs/OFFLINE_CPU_DEMO.md). Previously verified defense archives are never replaced by the CPU package builder.

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

Run `python scripts/verify_cpu_replay.py` for read-only CPU model replay, metrics recomputation, paired saved SHAP/LIME checks, fresh bounded explanation compatibility probes and all 15 scientific validation jobs. Run `python scripts/check_dashboard_cpu.py` to exercise both saved dashboard experiments with external Python connections blocked. Developer acceptance tools also include `scripts/browser_smoke_cpu.py` (real Edge browser) and `scripts/test_deployment_cpu.py --setup` (offline batch installation and launcher checks). Generate the CPU package with `python scripts/package_cpu_defense.py` after final checks. The original GPU packaging scripts remain as historical research tools; the CPU wizard does not use their GPU lock.

Scientific limits: retrospective adjustments/revisions; one fixed test split; no trading-cost/profitability backtest; sparse bounded explanation subsets; correlated-feature masking; no new human trust study. Poor or negative R2 and persistence wins are retained. Diagnostic fixes address demonstrated numerical errors, never tuning against the thesis's scores. See the complete defense script and committee Q&A in docs/.
