# CPU deployment report

Verified on Windows x64 with CPython 3.12.13, PyTorch 2.5.1+cpu and Streamlit 1.41.1 on 23 October 2026 (Asia/Baghdad).

## Root cause and repair

`main.py` was the default PyCharm `print_hi` sample. Streamlit served its shell but the script created no UI elements. The original application already existed at `dashboard/app.py`. The root entry point now runs that file with `runpy`, retaining its original eight tabs and architecture. The correct direct command is `python -m streamlit run main.py`; the supported Windows workflow is SETUP_DEMO.bat followed by START_DEMO.bat.

The original tabs remain Overview, Data & preprocessing, Forecasting, Compare models, Explain predictions, Regimes, Reproducibility and Thesis alignment. Local historical snapshot charts were added within preprocessing, saved forecast replay is labeled explicitly, and preserved scientific validation metrics/reports are available within Reproducibility. No replacement dashboard was created.

## Compatibility and evidence

The separate `requirements-cpu.txt` pins 89 dependency distributions. `wheelhouse-cpu` contains these 89 Windows x64/CPython 3.12 compatible wheels plus the project wheel (90 total). PyTorch is exactly 2.5.1+cpu; `torch.version.cuda is None` and CUDA availability is false. The original GPU lock, GPU requirements, YAML research configurations and CUDA-capable training code remain unchanged. Existing LSTM loading already uses `torch.load(..., map_location=device, weights_only=True)`; CPU verification explicitly requests `cpu`.

All four trained model types were loaded for AAPL, SP500, NASDAQ, GOLD, OIL and the separate monthly HOUSING index. Saved test predictions match CPU replay within the original verification tolerances. MAE, RMSE, MAPE and R² were recomputed against the authentic saved datasets. Saved SHAP reconstruction/background bounds and paired LIME target dates were checked for every model/dataset. Fresh bounded SHAP/LIME compatibility probes also ran on all four existing AAPL models, including CPU LSTM; these diagnostic probes do not replace scientific evidence.

All 15 supplemental scientific validation jobs replayed on CPU; 23,848 aggregate serialized prediction rows and 88 metric rows were verified. The existing cross-device LSTM tolerance remains eight FP32 epsilon units scaled by the training-target standard deviation. Original reported results and rankings were not altered. The dashboard displays saved evidence; live inference is exercised separately by the verification scripts.

The pre-repair preservation baseline covers 2,016 original files in runs, scientific validation, raw datasets and provider manifests. Every file matches its original SHA-256. Specifically protected: `full_20261021T040901084647Z` and `validation_20261021T055002439194Z`. No model retraining was used to repair the application. Existing unit tests include a small temporary training fixture, rather than retraining a research checkpoint.

## Executed checks

| Check | Executed result and evidence |
|---|---|
| Existing pytest suite | 33 passed, 1 skipped; `artifacts/deployment/pytest.xml` and `.log`. The skipped test requires CUDA hardware. |
| Application imports | All 39 discoverable `xai_finance` modules imported; `cpu_replay.json`. |
| Saved-model CPU replay and explanation probes | Passed for six datasets/four models and 15 supplemental jobs; `cpu_replay.json`. |
| Dashboard interactions | Both completed saved experiments, eight dataset/run combinations, all four models, first/last explanation date for each model, all eight tabs; `dashboard_final.json` and `windows_offline_dashboard.json`. |
| Real browser | Headless Microsoft Edge clicked each tab and checked visible content, charts and exception elements; eight screenshots per successful rehearsal. The installed CPU browser test also expanded scientific validation; `browser_cpu_installed/receipt.json`. |
| Fresh offline setup | SETUP_DEMO.bat --offline passed using a new `.demo_venv`; `windows_setup.json`, `windows_setup.log`. |
| Launcher | START_DEMO.bat passed health, occupied-port fallback, duplicate reuse, browser-open callback, actionable invalid-port error, stop and restart; `windows_deployment.json`. |
| Research preservation | All 2,016 original files unchanged; `original_evidence_sha256.json` and `preservation.json`. |
| Static checks | Ruff passed across main.py, dashboard, src, scripts and tests. |
| Extracted package installation | Fresh offline setup passed after extracting the candidate ZIP to `dist/CPU acceptance with spaces/Mohammad_XAI_Defense_CPU`, with no copied environment; `extracted_setup.json`, `extracted_setup.log`. |
| Extracted package launcher/UI | Occupied-port fallback (8571 to 8572), duplicate reuse, stop/restart and all saved dashboard interactions passed; `extracted_deployment.json`, `extracted_offline_dashboard.json`. Real Edge checked all eight tabs and scientific validation; `browser_extracted_package/receipt.json`. |
| Extracted package test suite | 33 passed, 1 CUDA-only skip in 20.82 seconds with external Python network blocked; `extracted_pytest.xml`, `extracted_pytest.log`. |
| Repeat setup | Passed against the installed source CPU environment and reused its running server; `repeated_setup_final.log`. |

External Python DNS/TCP connections were denied using the test-only `scripts/offline_guard/sitecustomize.py` in setup/launcher acceptance. Its enforcement was tested with a rejected connection to example.com. Separate dashboard and inference checks also denied external Python connections. Browser external HTTP(S) was routed to a closed loopback proxy with only localhost bypassed. No global Windows adapter/firewall settings were changed. This is a process-level offline rehearsal on this Windows host, not a test on Mohammad's physical computer or a claim that the entire operating system was disconnected.

The initial wheel-download CDN stalled; the official download.pytorch.org URL succeeded. An initial installation spent excessive time compiling Plotly bytecode and was stopped; the final fresh installation uses pip's `--no-compile` and passed. An initial browser rehearsal with a relative profile path failed; profile paths are now resolved to absolute paths and subsequent browser checks passed. These failures did not alter original research evidence.

## Windows workflow

SETUP_DEMO.bat checks Windows/Python compatibility, package and artifact integrity, dependencies, CPU model replay, SHAP/LIME, scientific validation, rendered UI and server health. It uses a separate `.demo_venv`, installs bundled wheels with `--no-index`, and writes diagnostics under `.demo_runtime/logs`. Python 3.12 must already be installed. The Python launcher, an existing project environment or an already installed uv-managed Python can bootstrap setup; XAI_PYTHON supports a custom Python path.

START_DEMO.bat uses that isolated environment and the root main.py. It opens the browser, reuses its own healthy process, and scans 20 local ports when the requested one is occupied. Ownership combines the exact folder, PID and Windows process creation timestamp. Stop terminates only that process and its verified descendants, including a possible Windows venv redirector child. Other services are left running. No administrator account, NVIDIA driver, CUDA, IDE or training is required.

## Packaging and transfer

The CPU package builder includes all original evidence files and all local research runs, including superseded diagnostics; no large research artifact is silently omitted. It includes the full scientific validation/source snapshot, raw data/manifests, checkpoints, saved predictions, SHAP/LIME artifacts, reports, tests, source, CPU wheels, wizards and offline instructions. Provider cookies, browser profiles, virtual environments, pip caches, Git metadata and older distribution archives are excluded. Prior research/defense archives are not overwritten; the builder refuses an existing output ZIP.

Every packaged file has a byte count and SHA-256 in CPU_PACKAGE_MANIFEST.json. The builder checks ZIP CRC and independently hashes every ZIP member before release, then writes a companion archive SHA-256 file. A virtual environment is never bundled or assumed portable. The Python installer is not bundled.

The tested candidate archive contained 2,305 files including its manifest (610,659,501 bytes), passed CRC and every member's SHA-256, and then passed fresh installation and browser/deployment acceptance after extraction to a path containing spaces. The final named distribution adds completed documentation and acceptance receipts; application source, pinned wheels and research evidence retain the tested content. **Use the companion `Mohammad_XAI_Defense_CPU.zip.sha256` outside the ZIP to verify the release archive.** Its exact bytes, SHA-256 and full member verification are also recorded in the build workspace's `artifacts/deployment/package.json` and `final_release.json`; those post-build release receipts are deliberately not bundled. The bundled `candidate_package.json` describes the tested candidate, not the release ZIP. The builder releases the final ZIP only after its CRC and all member hashes pass. The independent release check also extracts it afresh and confirms all executable code, wheels and original evidence match the tested candidate. No original verified archive is replaced.

Transfer `Mohammad_XAI_Defense_CPU.zip` and its `.zip.sha256` file. Install Windows x64 Python 3.12 beforehand, verify the ZIP hash, extract the entire ZIP to a writable local folder, double-click SETUP_DEMO.bat and then START_DEMO.bat. Use the local URL printed by the launcher. The bundled wheels support offline installation after Python is available. Detailed instructions: [OFFLINE_CPU_DEMO.md](OFFLINE_CPU_DEMO.md).

## Files changed

Modified: `.gitignore`, `main.py`, `dashboard/app.py`, `README.md`, `scripts/launch_demo.py`, `scripts/setup_offline.py`, `scripts/offline_demo.py`.

Added: `requirements-cpu.txt` (completed the pre-existing untracked CPU dependency draft), `SETUP_DEMO.bat`, `START_DEMO.bat`, `scripts/bootstrap_cpu.py`, `scripts/demo_wizard.py`, `scripts/check_dashboard_cpu.py`, `scripts/browser_smoke_cpu.py`, `scripts/verify_cpu_replay.py`, `scripts/verify_preservation_cpu.py`, `scripts/test_deployment_cpu.py`, `scripts/offline_guard/sitecustomize.py`, `scripts/package_cpu_defense.py`, `docs/OFFLINE_CPU_DEMO.md`, this report, CPU wheels, generated deployment receipts/logs/screenshots, the ZIP, and its checksum file.

## Limits

The demonstration replays saved evidence, rather than current prices or live market forecasts. Scientific limitations remain retrospective adjusted/revised data, housing publication-vintage uncertainty, exploratory supplemental tests, sparse explanation subsets and no new human trust study. Poor scores and persistence wins remain visible. Only this Windows host was tested; repeat setup and rehearse all eight tabs on Mohammad's computer before the defense. Moving a created virtual environment is unsupported; extract to the final location and run setup there. CUDA hardware diagnostics were skipped intentionally. Older historical GPU/offline packaging scripts are retained for research provenance; the CPU package uses package_cpu_defense.py and the CPU wizard.
