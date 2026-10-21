from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd

from xai_finance.config import ROOT
from xai_finance.storage import read_json, sha256
from xai_finance.validation.diagnostics import prediction_amplitudes
from xai_finance.validation.figures import LEARNED, generate_figures


def markdown_table(table: pd.DataFrame) -> str:
    formatted = table.copy()
    for column in formatted:
        formatted[column] = formatted[column].map(lambda entry: f"{entry:.6f}" if isinstance(entry, float) else str(entry))
    lines = ["| " + " | ".join(formatted.columns) + " |", "| " + " | ".join(["---"] * len(formatted.columns)) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in formatted.to_numpy().tolist())
    return "\n".join(lines)


def rmse_table(metrics: pd.DataFrame) -> str:
    order = LEARNED + ["Zero", "TrainMean", "LastObservedChangeOrReturn", "TrainMajorityDirectionMedianMagnitude"]
    pivot = metrics.pivot(index="asset", columns="model", values="rmse")
    pivot = pivot.reindex(columns=[name for name in order if name in pivot.columns]).rename(columns={"LinearRegression": "OLS", "RandomForest": "RF", "GradientBoosting": "GBM", "TrainMean": "Train mean", "LastObservedChangeOrReturn": "Last change/return", "TrainMajorityDirectionMedianMagnitude": "Train majority"})
    return markdown_table(pivot.reset_index())


def dataset_table(audits: dict) -> pd.DataFrame:
    rows = []
    for asset, audit in audits.items():
        dataset, split = audit["dataset"], audit["alignment"]["split"]
        rows.append({"asset": asset, "symbol": dataset["symbol"], "frequency": dataset["frequency"], "units": dataset["units"], "snapshot_start": dataset["first_date"], "snapshot_end": dataset["last_date"], "raw_n": dataset["rows"], "train_n": split["train"]["n"], "validation_n": split["validation"]["n"], "test_n": split["test"]["n"], "train_last_label": split["train"]["target_end"], "test_first_label": split["test"]["target_start"], "test_last_label": split["test"]["target_end"], "snapshot_sha256": dataset["sha256"]})
    return pd.DataFrame(rows)


def execution_summary(destination: Path) -> pd.DataFrame:
    rows = []
    for path in sorted((destination / "experiments").rglob("training.json")):
        design = read_json(path.parent / "design.json")
        lstm = read_json(path)["LSTM"]
        rows.append({**{name: design[name] for name in ["asset", "target", "design", "fold"]}, "device": lstm["device"], "precision": lstm["precision"]["effective_precision"], "batch_size": lstm["batch_size"], "best_epoch": lstm["selection"]["best_epoch"], "epochs_executed": lstm["selection"]["epochs_executed"], "training_seconds": lstm["training_seconds"], "training_label_cutoff": lstm["scaler_target_cutoff"]})
    return pd.DataFrame(rows)


def evidence_tables(destination: Path, original: Path) -> dict:
    audits = read_json(destination / "original_audit.json")
    datasets = dataset_table(audits)
    datasets.to_csv(destination / "dataset_definitions.csv", index=False)
    historic = pd.DataFrame(read_json(ROOT / "docs/thesis_reported_reference.json")["models"])
    historic.to_csv(destination / "thesis_reported_separate.csv", index=False)
    metrics = pd.read_csv(destination / "new_metrics.csv")
    amplitudes = prediction_amplitudes(pd.read_csv(destination / "new_predictions.csv"))
    amplitudes.to_csv(destination / "prediction_amplitudes.csv", index=False)
    training = execution_summary(destination)
    training.to_csv(destination / "training_execution_summary.csv", index=False)
    frozen = pd.read_csv(destination / "original_metrics_recalculated.csv")
    frozen.pivot(index="asset", columns="model", values="rmse").to_csv(destination / "frozen_level_rmse_separate.csv")
    generate_figures(original, destination)
    return {"audits": audits, "datasets": datasets, "historic": historic, "metrics": metrics, "frozen": frozen, "amplitudes": amplitudes, "training": training}


def principal_findings(evidence: dict) -> str:
    metrics = evidence["metrics"]
    learned = metrics[(metrics.design == "fixed_split") & metrics.model.isin(LEARNED)]
    point_wins = learned[learned.rmse_ratio_vs_zero < 1]
    favorable_intervals = learned[learned.mse_difference_ci_high < 0]
    walk = metrics[(metrics.design == "walk_forward") & metrics.model.isin(LEARNED)]
    walk_wins = walk[walk.rmse_ratio_vs_zero < 1]
    return f"The new fixed-split analyses produce {len(point_wins)} price-RMSE point improvements over zero change across {len(learned)} learned-model comparisons, but {len(favorable_intervals)} have an exploratory, unadjusted paired-bootstrap interval wholly favoring the model. Thus these results do not establish a reliable learned-model advantage. The walk-forward analysis has {len(walk_wins)} point improvements among {len(walk)} learned-model comparisons, reported separately below. Near-persistence performance after changing the target is a correction of a representation failure, not evidence that the thesis's LSTM ranking was reproduced."


def audit_narrative(evidence: dict, destination: Path) -> str:
    shift = pd.DataFrame([{ "asset": asset, "train_min": audit["shift"]["train_price_min"], "train_max": audit["shift"]["train_price_max"], "test_min": audit["shift"]["test_price_min"], "test_max": audit["shift"]["test_price_max"], "test_outside_fraction": audit["shift"]["test_price_outside_train_fraction"]} for asset, audit in evidence["audits"].items()])
    bounds = read_json(destination / "architecture_bounds.json")
    bound_table = pd.DataFrame([{"asset": asset, "LSTM_price_ceiling": row["price_upper_bound"], "RF_unavoidable_RMSE": row["random_forest_unavoidable_rmse_from_training_target_bounds"]} for asset, row in bounds.items()])
    return f"""## Audit of the frozen run

All six stored window matrices were rebuilt exactly from the hash-verified snapshots. Every label equals the next raw observed price, every final feature row equals the origin observation, and train/validation label observation dates precede or equal the next partition's first origin. The audit's label-availability boundary flag means this observation-index comparison; it does not independently establish publication timestamps or historical vintages. Deleting the future portion of each snapshot leaves all earlier engineered features exactly unchanged. No future interpolation or imputation is used. Rolling windows overlap across boundaries as legitimate historical context: for a one-observation horizon, an earlier label actually available at the later forecast origin does not require a 30-observation embargo.

Saved LSTM input and target scaler means, variances and scales match training-only recomputation exactly. Target scaling/inversion round trips were verified, including test targets outside the training range. Scaling does not restrict a test observation to the training range and no clipping is applied during normal prediction. The input scaler fits overlapping training-window rows, so observations receive repeated weights; this is documented training-only weighting, not future access. Linear regression has its own training-only flattened-input standardization and QR rank selection; the tree models use unscaled features. All saved models were reloaded on CPU and compared with the frozen predictions. Stored RMSE values were independently recomputed from frozen CSVs.

The information set assumes a forecast **after the origin session closes**, when that session's high, low, close and volume are known. This is a next-observation forecast, not a pre-close signal or an executable intraday trading strategy. Yahoo adjusted histories are retrospective snapshots; exact corporate-action vintages were not available. Monthly housing is revised and has release lags, so its chronology is only valid for the retrospective observation-index task, not real-time publication-date forecasting.

{markdown_table(shift)}

The 80/10/10 protocol fits models on training only, uses validation for selection/early stopping, and does not refit on train plus validation. Thus daily models have a roughly one-year gap between their final fitted label and the test period. This is intentional in the frozen specification and makes level extrapolation unusually demanding. Feature drift affects approximately half the test feature cells for the rising daily assets. Oil has no feature cells outside the training min/max box; its negative 2020 price remains intact. Change-target volatility also shifts: test versus training standard deviation is about 2.3 times higher for Apple and 3.2 times higher for gold, whereas oil's training dispersion is inflated by its historical shock. Exact level/change/return distribution summaries are in `target_distributions.csv`.

## Tree extrapolation and the LSTM ceiling

For a squared-error regression forest, each leaf is a mean of training targets; the ensemble is another average. Its predictions therefore stay within the training target range. The table gives the minimum possible RMSE of **any** predictor constrained to that range: the RMS distance of test targets to the training interval. This geometric diagnostic uses test outcomes for explanation only; it does not train or choose models.

{markdown_table(bound_table)}

For every actual test input, clipping each feature to its training minimum/maximum changed RF and GBM predictions by exactly zero. This follows the fitted trees' threshold partitions and directly demonstrates their inability to extend trends outside the feature box. GBM is an additive sum of residual trees: unlike RF, it is **not generally bounded by the original training target range**. Its fitted response remains piecewise constant beyond its split thresholds. The distinction matters when explaining extrapolation. See [the official decision-tree guide](https://scikit-learn.org/1.5/modules/tree.html) for the piecewise-constant extrapolation limitation.

The frozen LSTM also has a structural ceiling: at inference each last hidden coordinate is `output_gate * tanh(cell)` in [-1,1]; the linear head is bounded by `bias +/- sum(abs(weights))`. Inverse target scaling converts that interval into price units. These are valid global bounds, not necessarily jointly attainable extremes. Gold's ceiling is below most test prices; Apple, S&P 500 and Nasdaq also exceed their respective ceilings at the upper end. This explains a limitation of these **particular fitted networks**, not a theorem that all recurrent forecasters must fail. Optimization, target representation, validation regime, finite training budget and feature shift also matter.
"""


def experiment_narrative(evidence: dict, destination: Path) -> str:
    metrics = evidence["metrics"]
    fixed = metrics[metrics.design == "fixed_split"]
    delta = fixed[fixed.target == "price_change"]
    returns = fixed[fixed.target == "simple_return"]
    walk = metrics[metrics.design == "walk_forward"]
    walk_intervals = walk[walk.model.isin(LEARNED)][["asset", "model", "rmse_ratio_vs_zero", "mse_difference_ci_low", "mse_difference_ci_high"]]
    intervals = fixed[fixed.model == "LSTM"][["asset", "target", "rmse_ratio_vs_zero", "mse_difference_vs_zero", "mse_difference_ci_low", "mse_difference_ci_high"]]
    direction = delta[delta.model.isin(LEARNED + ["TrainMajorityDirectionMedianMagnitude"])][["asset", "model", "direction_accuracy", "direction_coverage"]]
    wins = fixed[fixed.model.isin(LEARNED) & (fixed.rmse_ratio_vs_zero < 1)]
    robust = wins[wins.mse_difference_ci_high < 0]
    amplitudes = evidence["amplitudes"]
    lstm_amplitudes = amplitudes[(amplitudes.design == "fixed_split") & (amplitudes.model == "LSTM")][["asset", "target", "observed_target_std", "predicted_target_std", "predicted_to_observed_std"]]
    training = evidence["training"]
    walk_epochs = training.loc[training.design == "walk_forward", "epochs_executed"].max()
    return f"""## New experiments: design and execution

These are exploratory sensitivity analyses: the original test outcomes were already known. The timestamped protocol was recorded before additional model training; no new test results were used to alter candidates, features, training budgets or reported outcomes. The protocol SHA256 is `{sha256(destination / 'protocol.json')}`. Target definitions, exclusions and budgets are retained in `protocol.json`.

All models retain the exact frozen 30-by-20 feature windows and chronological dates. The primary experiment changes only the label to `delta[t+1] = P[t+1] - P[t]`, then reconstructs `P_hat[t+1] = P[t] + delta_hat[t+1]`. It runs on all five daily assets, retaining the negative oil observation. A separate simple-return experiment uses `r[t+1] = P[t+1]/P[t] - 1` and reconstructs `P_hat[t+1] = P[t] * (1 + r_hat[t+1])` on the four strictly positive daily series. Oil returns are excluded by protocol, with no filtering or clipping of its change experiment. Features still include levels: these experiments do not claim to make the entire input process stationary.

OLS retains training-only scaling/QR rank selection. RF tries 100 trees with depth 5 or 10 and leaf size 3. GBM tries 100 trees with (depth 2, rate .03) or (depth 3, rate .1). Validation RMSE in the **new target units** selects the candidate; return RMSE selection weights errors differently from price RMSE. LSTM uses the original 32 hidden units, dropout .1, Adam .001, gradient clipping 1, at most 60 epochs and patience 8, training-only target/input scalers, no shuffling and identical fixed seed 42. AMP is enabled only if its training-fixture loss check is finite and within 5% of FP32. CUDA/CPU choice, actual precision, batch/VRAM probes, best/last checkpoints, epoch histories, scaler cutoffs, candidates and CPU reload checks are saved for every job. Price predictions are not truncated to historical bounds and returns are not constrained to force plausible results.

Four explicit naive target forecasts are included: zero (exact persistence after reconstruction), training mean (fixed drift), the most recent observed change/return, and the training-majority sign times the training median nonzero magnitude. The latter's magnitude is an explicit forecast convention, not an optimized trading strategy. Last-observation forecasts use the prior label, already known at the current origin; they do not use the unknown current test label. Mean and majority baselines are fitted using training labels only. Zero/drift methods are standard benchmarks; see [Forecasting: Principles and Practice](https://otexts.com/fpp3/simple-methods.html).

### Fixed-split price-change experiment: reconstructed-price RMSE

{rmse_table(delta)}

### Fixed-split simple-return experiment: reconstructed-price RMSE

{rmse_table(returns)}

The OLS change-target forecasts should be almost identical to the original price-target forecasts: with an intercept and the current price in the feature span, subtracting current price from the label and adding it back at prediction is an algebraic reparameterization. A difference in RF/LSTM behavior is therefore informative about representation and model constraints, rather than evidence that changing a target guarantees new information.

The following post-training diagnostic compares LSTM target-prediction dispersion with actual target dispersion. Low reconstructed-price error can arise from forecasting near-zero changes, which is close to persistence, without accurately predicting the day's fluctuation. It must not be presented as evidence that the network recovered a strong return signal. Full amplitudes, means and sample correlations for all models are in `prediction_amplitudes.csv`; these are descriptive, not new selection criteria.

{markdown_table(lstm_amplitudes)}

### Walk-forward validation

Two assets (Apple and S&P 500) receive three expanding-history refits, covering the original 271 test observations in contiguous disjoint blocks of 91, 90 and 90. Before each block, the latest 270 available labels are validation and all earlier labels are training. Each fold refits preprocessing, candidate selection and all four models from scratch. The first fold uses the original training/validation boundaries; later folds can use earlier test labels only once they are available. Forecasts within each block continue to use the actual latest observed feature history; parameters remain frozen until the next block. This is block walk-forward one-step prediction, not a 90-step recursive forecast.

The LSTM walk-forward cap is 30 epochs with patience 8; other settings and tabular candidate budgets are unchanged. The largest actual walk-forward epoch count is {walk_epochs}, with every job's actual device, precision, batch, best epoch and fitted-label cutoff exported in `training_execution_summary.csv`. Validation continues to reserve a 270-observation tail, so these refits reduce staleness incrementally but do not implement daily training or final train-plus-validation refitting. The caps differ from the fixed-split experiment and should not be conflated with a pure refit-frequency causal test. Label availability is explicitly asserted under the daily after-close assumption; general temporal validation motivation is described in [scikit-learn's temporal-split documentation](https://scikit-learn.org/1.5/modules/generated/sklearn.model_selection.TimeSeriesSplit.html).

{rmse_table(walk)}

{markdown_table(walk_intervals)}

### Directional accuracy and uncertainty

{markdown_table(direction)}

Directional accuracy compares three-way signs of predicted and observed price change. Nonzero coverage and accuracy conditional on an active forecast are also saved. Zero-change forecasts have 0% active coverage; their three-way score counts only exactly flat outcomes. They are **not a 0%-skill trading classifier**. Binary up/not-up accuracy is provided separately with zero mapped to not-up. Training-majority direction is the appropriate simple active comparator; 50% is not an assumed empirical baseline. Direction scores do not include trading costs, calibration or profitability.

{markdown_table(intervals)}

Each interval is a paired circular block bootstrap of daily `model squared price error - zero squared price error`, using block length 10, 2,000 resamples and seed 42. Negative differences favor the model. Price RMSE ratios below 1 occur in {len(wins)} of the {len(fixed[fixed.model.isin(LEARNED)])} learned-model/target/asset comparisons; {len(robust)} have an unadjusted interval entirely below zero. Intervals are exploratory, use one prespecified block length, do not include training uncertainty, and have no multiple-comparison correction. Nominal coverage depends on the blocks adequately representing serial dependence; nonstationarity and fold-dependent models can weaken that approximation. Marginal wins or intervals overlapping zero cannot establish reliable superiority. Cross-asset dependence and the shared test period also prevent treating these comparisons as independent replications.

All MAE, RMSE, MAPE, R², direction/coverage, target-unit errors and bootstrap details are in `new_metrics.csv/json`. Price MAPE uses nonzero actual prices with zero counts recorded; target MAPE is also exported for transparency, but near-zero returns/changes make it unstable and it is not a selection criterion. Price R² can remain very high for persistence because the level varies slowly; target R² and error relative to zero change are more informative about incremental forecast skill. No returns, price errors or metrics are pooled across incompatible asset units.
"""


def write_report(destination: Path) -> None:
    protocol = read_json(destination / "protocol.json")
    original = ROOT / "artifacts/runs" / protocol["original_run"]
    evidence = evidence_tables(destination, original)
    verification = read_json(destination / "verification.json")
    replication = read_json(destination / "determinism_replication/verification.json")
    precision = pd.read_csv(destination / "reconstruction_precision_comparison.csv")
    precision = precision.loc[precision.max_price_difference > 1e-8, ["asset", "model", "max_price_difference", "as_executed_rmse", "float64_rmse", "rmse_difference", "direction_predictions_changed"]]
    test_suite = ET.parse(destination / "tests_final.xml").getroot().find("testsuite")
    relative = destination.relative_to(ROOT).as_posix()
    frozen = evidence["frozen"].pivot(index="asset", columns="model", values="rmse").reset_index()
    report = f"""# Scientific validation report

Frozen run: `full_20261021T040901084647Z`. Additional validation: `{protocol['validation_id']}`. All new outputs are under `{relative}`. This review keeps the thesis's claims, frozen reconstruction and new exploratory experiments as separate evidence categories. No winner is assumed.

## Main conclusion

Persistence winning the five daily level-forecast benchmarks is a valid empirical outcome. The audit found no observation-index chronological leakage, label-shift error or inverse-scaling error in the frozen implementation. Point-in-time data correctness was not established: Yahoo adjustments are retrospective, and housing observation months are not release dates. Severe upward level shifts, fixed training cutoffs, tree extrapolation constraints and the particular fitted LSTM's bounded output explain much of the very large learned-model errors. Changing to change/return labels tests those constraints while preserving the information set. It does not create predictable daily return information or entitle LSTM to win.

{principal_findings(evidence)}

## Distinct datasets and result provenance

{markdown_table(evidence['datasets'][['asset', 'symbol', 'frequency', 'raw_n', 'train_n', 'validation_n', 'test_n', 'train_last_label', 'test_first_label', 'test_last_label']])}

Exact units, source symbols, snapshot dates and SHA256 hashes are in `dataset_definitions.csv` and `original_audit.json`. Daily sources are fixed Yahoo snapshots for 2015-01-01 inclusive through 2026-01-01 exclusive; gold/oil calendars differ from equities. Housing is the separate monthly FRED CSUSHPINSA series. New change/return training is restricted to daily assets; housing is audited and retained in the frozen table only.

### Thesis-reported values: historical claims, not reproduced observations

{markdown_table(evidence['historic'])}

Source: Chapter 4 section 4.2 Table 4, paragraphs P1026-P1049, figure P1050; TOC page 101, physical pagination unverified. The thesis does not supply the dataset, units, dates or saved runs needed to compare those numbers numerically with the new asset-specific metrics. Its appendix instead shows DecisionTree/XGBoost on missing `ether.csv`, a contemporaneous Close label and full-data mean imputation before splitting. These screenshots do not substantiate the four-model next-period result table. No assertion is made that the original Table 4 was produced by those screenshots, or that its underlying experiment necessarily leaked: the required evidence is absent. See `docs/THESIS_TRACEABILITY.md` and `docs/thesis_reported_reference.json`, both preserved unchanged.

### Frozen reconstructed price-level RMSE: independently recalculated

{markdown_table(frozen)}

Daily persistence wins all five assets. Monthly housing differs: OLS beats persistence. These numbers are retained in a separate CSV and are never replaced by the new experiments.

{audit_narrative(evidence, destination)}

{experiment_narrative(evidence, destination)}

## Verification and preservation

Executed {len(verification['jobs'])} additional training jobs, each containing four learned models and four naive baselines. Independently reloaded every learned model on CPU and replayed all {verification['aggregate_rows']:,} saved forecast rows; all {verification['aggregate_metric_rows']} aggregate metric records were recomputed from serialized predictions. Each job has hashes for its models, best/last checkpoints, histories, labels, splits and outputs. One AAPL change-target LSTM was retrained independently: all epoch training/validation losses and all {replication['test_n']} test predictions were bitwise identical on this machine. That is a same-environment reproducibility check, not a multi-seed robustness study.

An initial replay check used a fixed absolute tolerance across target units and failed for two near-zero Nasdaq change predictions. The maximum CPU/CUDA difference was 0.0000076294 index points. Diagnosis then replayed every LSTM on the original CUDA device: all 15 jobs' predictions matched their saved values **bitwise**. CPU differences were at most 0.0000000662 training-target standard deviations, below one FP32 machine epsilon at unit scale. CPU replay now uses an absolute bound of eight FP32 epsilons times the training target standard deviation, with zero relative tolerance; sklearn/baseline replay uses 1e-9 absolute/relative tolerance. This precision-aware verification change does not alter a model or empirical result. The initial failed log and all cross-device measurements remain in `replay_and_preservation.log` and `cross_device_diagnostics.json/log`.

A second verification attempt exposed a distinct, minor arithmetic effect: the LSTM target predictions are native FP32, so NumPy computes `1 + predicted_return` in FP32 before multiplying by the FP64 origin price. Exact replay must preserve that native dtype; casting the saved return to FP64 first produces slightly different implied prices. The failed attempt is retained in `replay_and_preservation_verified.log`; the successful full check is in `replay_and_preservation_final.log`. Both as-executed new result files remain untouched. A separate sensitivity calculation reconstructs **all** saved targets in FP64, without retraining, and saves `float64_reconstructed_predictions.csv`, `float64_reconstructed_metrics.csv` and provenance. Material differences are confined to these four LSTM return jobs:

{markdown_table(precision)}

The largest price-rounding difference is about 0.001394 Nasdaq index points; the largest absolute RMSE difference is about 0.000079 points. No directional predictions change. These are separately labeled numerical sensitivity results, not replacements for the as-executed tables above, and they do not establish learned-model superiority.

The complete automated suite executed {test_suite.attrib['tests']} tests, with {test_suite.attrib['failures']} failures, {test_suite.attrib['errors']} errors and {test_suite.attrib['skipped']} skips. New boundary tests cover return reconstruction/scaling, rejection of negative-price returns, known-label naive forecasts, disjoint walk-forward blocks and directional abstention. Logs and JUnit XML are isolated in this validation directory. See `verification.json`, `tests_final.xml`, `tests_final.log` and `determinism_replication/verification.json`.

All {verification['preservation']['protected_files']:,} files in the pre-review preservation inventory retained their byte counts and SHA256 hashes. This includes the original run and checkpoints, previous result/verification files, input snapshots, thesis, existing source/configuration and verified offline defense package. The original defense ZIP SHA256 remains `{verification['preservation']['offline_zip_sha256']}`. No original result or package was overwritten; this validation is an additive supplement.

## Figures and defense explanation

New publication exports (PNG and SVG) are in this run's `figures/` directory: `frozen_level_predictions`, `target_representation_rmse`, `paired_uncertainty`, `walk_forward_cumulative_loss`, and `directional_accuracy`. The existing figures and offline package remain untouched. The separate `offline_validation.html` embeds these charts for an offline defense explanation.

Suggested oral explanation: “The historical thesis ranks LSTM first but omits the experimental details needed for exact replication. Our transparent next-observation benchmark includes persistence and reveals that level models struggle when test prices rise beyond training support. We verified chronology and scaling, then ran controlled change/return targets and expanding-history validation. These reduce representation-related failures, but the evidence does not justify declaring a universal winner. We report uncertainty and all outcomes rather than tuning to the thesis.”

## Remaining limitations and next research priority

- These analyses reuse an observed test period. A genuinely unseen subsequent period or new prespecified historical holdout is needed for confirmatory comparison; repeatedly choosing models from these test tables would contaminate future claims.
- One seed, one 30-session lookback, two tree candidates, small recurrent networks and fixed epoch budgets do not establish architecture-wide rankings. Stronger regularization, dimensionless relative-price features, train-plus-validation refitting and shorter trailing validation windows are reasonable future experiments, not retrospectively applied fixes.
- Walk-forward covers only two equity series and three refits; validation preserves a 270-session tail. This is a feasibility-bounded sensitivity analysis, not exhaustive daily retraining or cross-market confirmation.
- Yahoo retrospective adjustments, continuous-futures rolls and the negative oil observation limit economic interpretation. Oil change targets remain numerically valid but its extreme training shock affects the loss distribution. Monthly housing lacks vintage/release information and is not a real-time forecasting claim.
- MAPE around zero, level R², directional abstention, unadjusted intervals and cross-asset dependence require the qualifications above. No transaction-cost, trading-profit, probability calibration or causal conclusions are established.
- Existing SHAP/LIME artifacts explain the frozen **level models**. They were preserved and are not relabeled as explanations of newly trained return/change models. Marginal perturbations of correlated financial indicators can be off-manifold; predictive fit and explanation plausibility do not validate human trust or causality. No survey responses were invented.

The next priority is an independently held-out, predeclared comparison of parsimonious relative-price/return features with zero/drift benchmarks and a final-refit policy, followed by multiple seeds and cost-aware trading evaluation if trading claims are intended. The current evidence supports a defensible audit and exploratory comparison, not rewriting the thesis's historical numbers.
"""
    (destination / "SCIENTIFIC_VALIDATION_REPORT.md").write_text(report, encoding="utf-8")
    canonical = ROOT / "docs/SCIENTIFIC_VALIDATION_REPORT.md"
    if not canonical.exists():
        canonical.write_text(report, encoding="utf-8")
