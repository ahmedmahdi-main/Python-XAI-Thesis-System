# Codex Master Implementation Plan — Rebuilding Mohammad Saleh's Python XAI Thesis System

## Mission and academic integrity
Reconstruct a complete, genuinely executable, reproducible Python research framework aligned with Mohammad Saleh's thesis, *Developing an Explainable Artificial Intelligence (XAI) Framework for Stock Market Trend Prediction and Analysis*. Four-day deadline. Implement, test, execute and document. Do **not** reverse-engineer, fabricate, hardcode, or tune against the thesis's reported numerical results. Preserve them in a distinct historical reference file marked `THESIS_REPORTED_NOT_REPRODUCED`. Recomputed metrics must emerge from actual runs. Never fabricate survey participants or label simulated feedback empirical. Disclose deviations and gaps.

## Source-derived requirements
- Dataset categories: stock market (S&P 500, NASDAQ, individual equities), commodities (oil, gold, potentially silver/agricultural) and real estate series where a defensible public historical dataset is available.
- Public data providers discussed: Yahoo Finance, Quandl/Nasdaq Data Link, government databases. Use actual reproducible downloaded snapshots and manifests, provider name, symbol, date range, timezone, price adjustment convention, retrieval date, licenses and sha256.
- Features: OHLCV, simple and exponential moving averages, RSI, MACD, Bollinger Bands, lagged returns, volatility, momentum; economic indicators only if available and lagged by release/availability date.
- Models: Linear Regression, Random Forest Regressor, LSTM, Gradient Boosting Regressor. Prefer scikit-learn GBM for paper-faithful core; XGBoost only optional extension, not replacement.
- Explicit chronological train/validation/test split 80/10/10, no random split. Configurable window length for LSTM; common aligned evaluation timestamps and same historical feature information for all models.
- Metrics MAE, RMSE, MAPE, R2 on original target units; report direction accuracy as a secondary metric, since thesis title addresses trends. Include naive persistence and/or drift baseline as additional clearly labeled baselines (not replacements for original four models).
- XAI: SHAP and LIME, global feature importance, SHAP summary/beeswarm, waterfall, dependence, LIME local plots, comparison; optional Integrated Gradients for LSTM as a scope-controlled extension.
- XAI quality: stability, fidelity, performance overhead; explanations do not automatically improve accuracy/trust.
- Thesis reported reference values: Linear Regression (MAE 1.23, RMSE 1.67, R2 .65); Random Forest (.85,1.10,.80); LSTM (.76,1.02,.85); Gradient Boosting (.82,1.05,.82). No unit or actual dataset fully specified; these MUST NOT be silently described as newly reproduced. Thesis also states survey percentages 78/85/70; raw responses, counts and protocols absent, so display only as historical claims with explicit unverifiable status.

## First action: audit the actual source document
1. Read the attached thesis locally. Focus on Persian chapter 4 sections 3.1–3.6, 4.1–4.4, the existing Table 4, survey conclusions, and appendix. Record exact page/section/quotation anchors, not fabricated page numbers. Review whether the source contains supplementary datasets or code paths.
2. Create `docs/THESIS_TRACEABILITY.md` with rows: source requirement; source chapter/page; intended module/config; acceptance evidence; exact/not specified; status. Create `docs/ASSUMPTIONS_AND_DEVIATIONS.md` to list missing source values and chosen research defaults.
3. Never rewrite original thesis evidence to fit the fresh runs. If reconstruction differs, produce a proposed amendment for the academic text, keeping a clear historical-versus-new boundary.

## Proposed project tree
```
xai-finance-thesis/
  README.md
  pyproject.toml
  requirements-lock.txt
  .env.example
  Makefile
  configs/
    default.yaml
    quick_demo.yaml
    full_experiment.yaml
    datasets.yaml
  data/
    raw/.gitkeep
    processed/.gitkeep
    manifests/.gitkeep
  src/xai_finance/
    __init__.py
    config.py
    seed.py
    io/data_sources.py
    io/cache.py
    data/validate.py
    data/preprocess.py
    data/features.py
    data/split.py
    data/windows.py
    models/baselines.py
    models/sklearn_models.py
    models/lstm_model.py
    models/search.py
    evaluate/metrics.py
    evaluate/walk_forward.py
    evaluate/regimes.py
    explain/shap_explain.py
    explain/lime_explain.py
    explain/quality.py
    explain/format.py
    reports/plots.py
    reports/tables.py
    reports/render.py
    pipelines/train.py
    pipelines/explain.py
    pipelines/benchmark.py
    pipelines/report.py
    cli.py
  dashboard/app.py
  tests/
    test_no_leakage.py
    test_labels.py
    test_splits.py
    test_feature_causality.py
    test_metrics.py
    test_model_alignment.py
    test_explain_consistency.py
    test_smoke_pipeline.py
  artifacts/
    models/.gitkeep
    results/.gitkeep
    plots/.gitkeep
    explanations/.gitkeep
  docs/
    THESIS_TRACEABILITY.md
    ASSUMPTIONS_AND_DEVIATIONS.md
    METHODOLOGY.md
    REPRODUCIBILITY.md
    DEMO_SCRIPT.md
    DEFENSE_QA.md
    RECONSTRUCTED_RESULTS.md
    4_DAY_PROGRESS.md
  scripts/
    verify_environment.py
    download_data.py
    run_quick.py
    run_full.py
    generate_defense_package.py
```

## Dataset protocol — critical
1. Configurable core experiment: primary S&P 500 index (`^GSPC`) and/or a single liquid equity (e.g., `AAPL`) with historical daily OHLCV; choose and clearly declare exact target. Secondary datasets: `^IXIC`, gold (`GC=F`), crude oil (`CL=F`) where viable. For real estate, use a publicly available documented monthly house-price index (e.g., FRED USSTHPI or CSUSHPINSA) and a **separate monthly-frequency experiment**. Do not pretend daily features/volume exist for a monthly house-price index.
2. Use explicit fixed start and end dates that yield sufficient history and end no later than retrieval date. Pin snapshot CSV/parquet and sha256. Do not replace a data source with simulated data without visible DEMO_ONLY labeling.
3. Validate schema, timestamps, duplicate dates, ascending order, numerical fields, OHLC sanity, trading gaps, missing-volume and corporate-action conventions. Never forward-fill target through market-closed days or interpolate using future observations. Drop unresolved rows with documented counts.
4. Define prediction at end of time t: forecast adjusted close at t+1 using only information genuinely available at close t; optionally secondary next-day return and direction = sign(close[t+1]-close[t]). If splitting across multiple tickers, do not mix asset magnitudes in a single unscaled result table. Preserve time-aligned lagged features. Timestamp every prediction with feature cutoff and target date.
5. Compute technical indicators using trailing windows only; fit transforms (scalers/imputers) on training observations only. For cross-validation refit all transforms inside each training fold. All validation and test transformations are frozen.
6. Derive windows after chronological partitioning with context allowed from past data only, ensuring target labels never cross from training into validation/test. Compute common sample intersection for fair model comparison.
7. 80/10/10 chronological split is mandatory for core results. Walk-forward folds are sensitivity analysis and must not be confused with the held-out test. Final test used once after selection, no tuning or model picking against it.

## Model specification
- Naive persistence: yhat[t+1]=close[t]; optional seasonal naive if justified; report for leakage/difficulty check.
- LinearRegression: sklearn Pipeline with appropriate feature scaling, report intercept/coefficients and feature list.
- RandomForestRegressor: tune n_estimators [100, 200], max_depth [5, 10, None], min_samples_leaf [1, 3]; deterministic random_state and n_jobs configured.
- GradientBoostingRegressor: n_estimators [100, 200], learning_rate [.03, .1], max_depth [2, 3]; deterministic random_state. Record actual selected config.
- LSTM: TensorFlow/Keras with input (batch, lookback, num_features); start lookback 30, 60; layers LSTM(32 or 64), dropout 0.1–0.2, Dense(1); optimizer Adam, loss MSE, EarlyStopping(monitor='val_loss',patience=8,restore_best_weights=True), ModelCheckpoint. Batch [32,64], max epochs 40–60 (quick mode <=10). Strict target inverse-transform before metrics. Disable shuffling across sequence windows for clarity (`shuffle=False`), seed numpy/python/tensorflow and log nondeterminism.
- Tune ONLY on validation / time-series CV, keeping a small compute budget. Save model, scaler, features, window length, training config, dependency versions and fitted cutoff.
- Acknowledge on random-walk price levels R2 may look high even without useful investment predictive power. Report naive baseline, directional accuracy and actual vs predicted plot.

## XAI implementation details
- Explain tree models with shap.TreeExplainer, model outputs in original target units; validate expected-value plus sum of attributions approximately matches forecast where applicable. Explain linear model using coefficients and SHAP LinearExplainer if supported.
- LIME TabularExplainer on tabular models using training-only background: `mode='regression'`, local seeded sampling and correct predict_fn, display feature range/weight/predicted value.
- For LSTM, provide SHAP via a compatible bounded-background Kernel/Permutation route on an adapter `predict_flat(X_2d)` that reshapes from `(n, lookback * features)` to `(n, lookback, features)` and returns the *correct original target scale*; budget 10–30 explained samples in full run and 1–3 in quick. If computationally prohibitive, document and supply integrated gradients as optional, never label a tree-model explanation as an LSTM explanation.
- Aggregate flattened LSTM attributions to both feature-by-time heatmap and sum of absolute values per original feature across lags; specify semantics. Do not equate SHAP attribution with causation.
- Produce local explanations for the SAME held-out test observation using SHAP and LIME for comparable models; a single chart must identify exact asset, prediction date, model, baseline and units. Build global feature ranking on a fixed declared test subset.
- XAI fidelity: compare model output with reconstructed SHAP expected+attribution and/or LIME surrogate output; stability under small plausible feature perturbations and rerun seeds, rank-correlation/top-k overlap; execution time. Measure rather than claim trust improvement.
- Chart export PNG/SVG/HTML; static matplotlib guaranteed for defense when offline.

## Quantitative evaluation and market regime analysis
- Compute MAE, RMSE, MAPE with nonzero-target guard, R2 in *unscaled* price units. Include sMAPE if appropriate but mark supplementary. Add one-step price-change directional accuracy, up/down confusion matrix, precision/recall for upward moves only where class counts meaningful.
- Report per-asset and per-model tables; do not average raw MAEs across assets with different units. Include train/validation/test counts, date intervals, runtime, params and seed.
- Define bull/bear/sideways regimes **a priori** using trailing return of preceding 20 trading days and fixed thresholds (example +5%, -5%, otherwise sideways) that only use data observable at prediction time. Record threshold and distribution. Compute per-regime errors, class counts and explanatory driver comparisons. Do not claim particular regime winners unless empirical runs show it.
- Generate predicted vs actual, error time-series, bar charts of MAE/RMSE/R2, loss curves, SHAP summary/waterfall/dependence, LIME individual decision, regime-specific performance and top-10 feature importance.
- Compare XAI to non-XAI forecasting via exact same fixed fitted model: adding post-hoc explanation cannot change prediction if inference remains untouched; use a regression test to verify unchanged `y_pred`. A separate refit/feature-selection experiment may affect accuracy but label accordingly.

## Survey and trust evidence
- Existing thesis text lists 78%, 85%, 70% but raw data / N / questionnaires cannot be verified. Create `docs/SURVEY_EVIDENCE_STATUS.md` stating these are unverified historical claims. Do not generate fake participants, responses, or statistical significance.
- Optional: ready-to-use Persian/Arabic/English 5-point Likert template with informed consent and anonymized CSV schema, designed to collect *new genuine data* if feasible; separate actual collection from demo. No claim of human trust enhancement unless collected and evaluated.

## Dashboard (functional defense demo)
Build Streamlit app with tabs:
1) Research Overview: thesis question, research flow, inputs, outputs, reference-vs-recomputed caution.
2) Data & Preprocessing: provider, symbol, range, train-val-test plots, missingness, derived features, feature cutoff.
3) Forecasting: select asset and model, actual vs predicted on TEST, metrics table, next-step forecast clearly tagged unverified until actual future close; prohibit future leakage.
4) Compare Models: four models + naive baseline, metrics and runtime on common dates.
5) Explain Predictions: select held-out date and model, SHAP local/global, LIME, financial-feature interpretation and disclaimers.
6) Regimes: bull/bear/sideways, counts, errors, drivers.
7) Reproducibility: hashes, manifests, config, software versions, test summary, artifacts export and known limitations.
8) Thesis Alignment: side-by-side thesis-reported table vs reproduced results with separate labels and mismatches; historic survey figures tagged unverified, NOT simulated as observed.
App must run from saved local artifacts without live internet once dataset snapshot and models are saved. Graceful errors for missing artifacts; helpful `python ...` command displayed.

## Commands and technical stack
- Python 3.11 (pin chosen runtime); pandas, numpy, scikit-learn, tensorflow-cpu (or TensorFlow compatible with environment), shap, lime, yfinance, matplotlib, plotly, streamlit, scipy, pyyaml, joblib, pyarrow, pytest, tqdm, packaging. Optional fredapi/nasdaqdatalink and captum only when relevant; do not introduce PyTorch unless essential. Pin workable versions in lock output, test on operating system.
- CLI:
  - `python -m xai_finance.cli doctor`
  - `python -m xai_finance.cli download --config configs/default.yaml`
  - `python -m xai_finance.cli validate --config configs/default.yaml`
  - `python -m xai_finance.cli train --config configs/quick_demo.yaml`
  - `python -m xai_finance.cli train --config configs/full_experiment.yaml`
  - `python -m xai_finance.cli explain --config configs/full_experiment.yaml`
  - `python -m xai_finance.cli evaluate --config configs/full_experiment.yaml`
  - `python -m xai_finance.cli report --config configs/full_experiment.yaml`
  - `streamlit run dashboard/app.py`
  - `pytest -q`
Actual CLI signature may change only if README and smoke tests are updated consistently.

## Acceptance gates and required tests
- A: No leakage: features for timestamp t invariant when records after t are altered; scaler fit cutoff inside train; labels/sequence indices respect boundaries; no random splitting; test target beyond feature cutoff.
- B: Baselines and metrics unit checked with small hand-computable series; MAPE 0-denominator controlled; model evaluation uses same held-out rows/dates; verify inverse transforms.
- C: Saving/reloading models reproduces forecasts within tolerance on a fixed local fixture; inference offline; cannot silently retrain on test.
- D: SHAP reconstruction matches same model prediction within method-appropriate tolerance, LIME predict function supports batches, background training-only, graph labels match actual target and unit.
- E: Main 4 models each train and evaluate successfully; artifacts include per-model predictions.csv, metrics.json, model file, configs, charts and environment metadata.
- F: Quick mode completes on CPU in practical time; full mode logs elapsed and checkpoint progress. If full training fails, leave clear partial result and do not mark it as complete.
- G: No historical reference metric is entered as a computed metric. Provenance test checks historical and fresh outputs are separate files with distinct labels.
- H: Demo can answer: why this forecast, what features matter, how predictions compare, how split and leakage are handled, where source data come from, why LSTM may or may not win on new run, what survey claims cannot currently be reproduced.

## Four-day schedule / priorities
Day 1 (first 8-12h): source audit, traceability, project scaffolding, versions, primary equity + index data snapshot, reproducible feature pipeline, leakage tests, naive/linear/RF/GBM baseline, preliminary results, no UI polish.
Day 2: LSTM training, tuning within allocated budget, held-out metrics, 80/10/10 verification, charts, walk-forward optional if time; store all artifacts and first end-to-end experiment.
Day 3: SHAP/LIME implementations, bounded LSTM explanation, attribution checks, regimes, Streamlit dashboard, offline saved-artifact demo. Begin defensible scientific interpretation of newly computed results.
Day 4: add commodities, and separate monthly real estate experiment only if data available; run full suite, consolidate figures and Persian/Arabic defense notes, discrepancy analysis vs thesis table, generate final defense folder, rehearse complete offline demonstration, create zipped versioned backup on two media/cloud locations. Cut secondary assets ahead of core completeness if behind.

## Deliverables that must exist
- Executable Python source, dependency lock, fully saved datasets with provenance and hashes, saved four trained models, cleaned experiment configs, automated tests, proper academic diagrams and figures, actual resulting CSV/JSON metrics, explainability exports, Streamlit dashboard, English technical README plus brief Persian defense guide, limitation/deviation log, 10-minute demonstration script, committee Q&A, reproducibility protocol, and single-command demo script.
- Build one `defense_package/` folder containing all needed assets and verify it on a clean Python environment or at least a clean venv without any Internet requirement for app viewing.
- Include a `RESULTS_AUDIT.md` stating each claim, file path, computed or thesis-reported status, dataset, run ID, units and evidence.

## Codex operating instructions
Implement in incremental vertical slices and run commands; do not just generate pseudo-code or a plan. Report after each slice which modules were created, commands actually executed, test pass/fail, actual metrics produced and blockers. Do not announce DONE without the project smoke test passing. Fix errors autonomously, record assumptions rather than hiding missing specifics. Prioritize scientific validity, auditability and offline presentation over superficial dashboard appearance. Document source citations to actual thesis pages/sections. Use typed Python interfaces, configurable settings, error handling, deterministic seeds where supported, lightweight tests, readable modules and reproducible saved artifacts. If data download cannot be completed, stop and request legitimate CSV snapshots or implement a clearly flagged `DEMO_ONLY_SYNTHETIC_DATA` mode solely for code testing; never substitute synthetic data for dissertation results. Do not alter original source file.

## Final Codex response format
1. Completion matrix with actual status per deliverable and file path.
2. Run commands verified on this machine, Python/package versions and OS.
3. Data snapshots, symbols, dates, hashes and observation counts.
4. Actual empirical metrics for each model/asset with data scale and test dates.
5. SHAP/LIME generated output locations and checks.
6. Tests passed/failed and unresolved scientific risks.
7. Differences from thesis historical table / survey figures; recommend text corrections if needed.
8. Offline demo instructions and backup location.
