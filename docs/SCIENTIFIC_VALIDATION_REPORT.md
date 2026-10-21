# Scientific validation report

Frozen run: `full_20261021T040901084647Z`. Additional validation: `validation_20261021T055002439194Z`. All new outputs are under `artifacts/scientific_validation/validation_20261021T055002439194Z`. This review keeps the thesis's claims, frozen reconstruction and new exploratory experiments as separate evidence categories. No winner is assumed.

## Main conclusion

Persistence winning the five daily level-forecast benchmarks is a valid empirical outcome. The audit found no observation-index chronological leakage, label-shift error or inverse-scaling error in the frozen implementation. Point-in-time data correctness was not established: Yahoo adjustments are retrospective, and housing observation months are not release dates. Severe upward level shifts, fixed training cutoffs, tree extrapolation constraints and the particular fitted LSTM's bounded output explain much of the very large learned-model errors. Changing to change/return labels tests those constraints while preserving the information set. It does not create predictable daily return information or entitle LSTM to win.

The new fixed-split analyses produce 6 price-RMSE point improvements over zero change across 36 learned-model comparisons, but 0 have an exploratory, unadjusted paired-bootstrap interval wholly favoring the model. Thus these results do not establish a reliable learned-model advantage. The walk-forward analysis has 1 point improvements among 8 learned-model comparisons, reported separately below. Near-persistence performance after changing the target is a correction of a representation failure, not evidence that the thesis's LSTM ranking was reproduced.

## Distinct datasets and result provenance

| asset | symbol | frequency | raw_n | train_n | validation_n | test_n | train_last_label | test_first_label | test_last_label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | AAPL | daily | 2766 | 2162 | 270 | 271 | 2023-11-02 | 2024-12-02 | 2025-12-31 |
| SP500 | ^GSPC | daily | 2766 | 2162 | 270 | 271 | 2023-11-02 | 2024-12-02 | 2025-12-31 |
| NASDAQ | ^IXIC | daily | 2766 | 2162 | 270 | 271 | 2023-11-02 | 2024-12-02 | 2025-12-31 |
| GOLD | GC=F | daily | 2766 | 2162 | 270 | 271 | 2023-11-07 | 2024-12-04 | 2025-12-31 |
| OIL | CL=F | daily | 2766 | 2162 | 270 | 271 | 2023-11-06 | 2024-12-04 | 2025-12-31 |
| HOUSING | CSUSHPINSA | monthly | 468 | 338 | 42 | 43 | 2018-11-01 | 2022-06-01 | 2025-12-01 |

Exact units, source symbols, snapshot dates and SHA256 hashes are in `dataset_definitions.csv` and `original_audit.json`. Daily sources are fixed Yahoo snapshots for 2015-01-01 inclusive through 2026-01-01 exclusive; gold/oil calendars differ from equities. Housing is the separate monthly FRED CSUSHPINSA series. New change/return training is restricted to daily assets; housing is audited and retained in the frozen table only.

### Thesis-reported values: historical claims, not reproduced observations

| model | mae | rmse | r2 |
| --- | --- | --- | --- |
| LinearRegression | 1.230000 | 1.670000 | 0.650000 |
| RandomForest | 0.850000 | 1.100000 | 0.800000 |
| LSTM | 0.760000 | 1.020000 | 0.850000 |
| GradientBoosting | 0.820000 | 1.050000 | 0.820000 |

Source: Chapter 4 section 4.2 Table 4, paragraphs P1026-P1049, figure P1050; TOC page 101, physical pagination unverified. The thesis does not supply the dataset, units, dates or saved runs needed to compare those numbers numerically with the new asset-specific metrics. Its appendix instead shows DecisionTree/XGBoost on missing `ether.csv`, a contemporaneous Close label and full-data mean imputation before splitting. These screenshots do not substantiate the four-model next-period result table. No assertion is made that the original Table 4 was produced by those screenshots, or that its underlying experiment necessarily leaked: the required evidence is absent. See `docs/THESIS_TRACEABILITY.md` and `docs/thesis_reported_reference.json`, both preserved unchanged.

### Frozen reconstructed price-level RMSE: independently recalculated

| asset | GradientBoosting | LSTM | LinearRegression | Persistence | RandomForest |
| --- | --- | --- | --- | --- | --- |
| AAPL | 52.548104 | 61.414866 | 4.571582 | 4.189369 | 51.403976 |
| GOLD | 1495.319590 | 1315.520559 | 55.789309 | 47.149802 | 1487.179158 |
| HOUSING | 112.781128 | 99.557614 | 1.158773 | 2.018202 | 114.184249 |
| NASDAQ | 5202.730176 | 3597.900440 | 311.695246 | 278.421187 | 5117.832703 |
| OIL | 1.382298 | 1.383632 | 1.691716 | 1.282035 | 1.324714 |
| SP500 | 1570.281033 | 980.470201 | 74.590237 | 65.821692 | 1542.689376 |

Daily persistence wins all five assets. Monthly housing differs: OLS beats persistence. These numbers are retained in a separate CSV and are never replaced by the new experiments.

## Audit of the frozen run

All six stored window matrices were rebuilt exactly from the hash-verified snapshots. Every label equals the next raw observed price, every final feature row equals the origin observation, and train/validation label observation dates precede or equal the next partition's first origin. The audit's label-availability boundary flag means this observation-index comparison; it does not independently establish publication timestamps or historical vintages. Deleting the future portion of each snapshot leaves all earlier engineered features exactly unchanged. No future interpolation or imputation is used. Rolling windows overlap across boundaries as legitimate historical context: for a one-observation horizon, an earlier label actually available at the later forecast origin does not require a 30-observation embargo.

Saved LSTM input and target scaler means, variances and scales match training-only recomputation exactly. Target scaling/inversion round trips were verified, including test targets outside the training range. Scaling does not restrict a test observation to the training range and no clipping is applied during normal prediction. The input scaler fits overlapping training-window rows, so observations receive repeated weights; this is documented training-only weighting, not future access. Linear regression has its own training-only flattened-input standardization and QR rank selection; the tree models use unscaled features. All saved models were reloaded on CPU and compared with the frozen predictions. Stored RMSE values were independently recomputed from frozen CSVs.

The information set assumes a forecast **after the origin session closes**, when that session's high, low, close and volume are known. This is a next-observation forecast, not a pre-close signal or an executable intraday trading strategy. Yahoo adjusted histories are retrospective snapshots; exact corporate-action vintages were not available. Monthly housing is revised and has release lags, so its chronology is only valid for the retrospective observation-index task, not real-time publication-date forecasting.

| asset | train_min | train_max | test_min | test_max | test_outside_fraction |
| --- | --- | --- | --- | --- | --- |
| AAPL | 20.548145 | 193.567078 | 171.365952 | 285.413116 | 0.977860 |
| SP500 | 1829.079956 | 4796.560059 | 4982.770020 | 6932.049805 | 1.000000 |
| NASDAQ | 4266.839844 | 16057.440430 | 15267.910156 | 23958.470703 | 0.985240 |
| GOLD | 1050.800049 | 2069.399902 | 2608.100098 | 4552.700195 | 1.000000 |
| OIL | -37.630001 | 123.699997 | 55.270000 | 80.040001 | 0.000000 |
| HOUSING | 75.132000 | 205.339000 | 292.671000 | 331.564000 | 1.000000 |

The 80/10/10 protocol fits models on training only, uses validation for selection/early stopping, and does not refit on train plus validation. Thus daily models have a roughly one-year gap between their final fitted label and the test period. This is intentional in the frozen specification and makes level extrapolation unusually demanding. Feature drift affects approximately half the test feature cells for the rising daily assets. Oil has no feature cells outside the training min/max box; its negative 2020 price remains intact. Change-target volatility also shifts: test versus training standard deviation is about 2.3 times higher for Apple and 3.2 times higher for gold, whereas oil's training dispersion is inflated by its historical shock. Exact level/change/return distribution summaries are in `target_distributions.csv`.

## Tree extrapolation and the LSTM ceiling

For a squared-error regression forest, each leaf is a mean of training targets; the ensemble is another average. Its predictions therefore stay within the training target range. The table gives the minimum possible RMSE of **any** predictor constrained to that range: the RMS distance of test targets to the training interval. This geometric diagnostic uses test outcomes for explanation only; it does not train or choose models.

| asset | LSTM_price_ceiling | RF_unavoidable_RMSE |
| --- | --- | --- |
| AAPL | 251.899103 | 46.646616 |
| SP500 | 6635.210640 | 1473.804926 |
| NASDAQ | 22421.782505 | 4847.450941 |
| GOLD | 2672.002963 | 1434.769361 |
| OIL | 144.852497 | 0.000000 |
| HOUSING | 278.390379 | 110.996055 |

For every actual test input, clipping each feature to its training minimum/maximum changed RF and GBM predictions by exactly zero. This follows the fitted trees' threshold partitions and directly demonstrates their inability to extend trends outside the feature box. GBM is an additive sum of residual trees: unlike RF, it is **not generally bounded by the original training target range**. Its fitted response remains piecewise constant beyond its split thresholds. The distinction matters when explaining extrapolation. See [the official decision-tree guide](https://scikit-learn.org/1.5/modules/tree.html) for the piecewise-constant extrapolation limitation.

The frozen LSTM also has a structural ceiling: at inference each last hidden coordinate is `output_gate * tanh(cell)` in [-1,1]; the linear head is bounded by `bias +/- sum(abs(weights))`. Inverse target scaling converts that interval into price units. These are valid global bounds, not necessarily jointly attainable extremes. Gold's ceiling is below most test prices; Apple, S&P 500 and Nasdaq also exceed their respective ceilings at the upper end. This explains a limitation of these **particular fitted networks**, not a theorem that all recurrent forecasters must fail. Optimization, target representation, validation regime, finite training budget and feature shift also matter.


## New experiments: design and execution

These are exploratory sensitivity analyses: the original test outcomes were already known. The timestamped protocol was recorded before additional model training; no new test results were used to alter candidates, features, training budgets or reported outcomes. The protocol SHA256 is `634aa749bc828b8a06589d09a40d271d627472faf8da9f30a03e3cfca37de07c`. Target definitions, exclusions and budgets are retained in `protocol.json`.

All models retain the exact frozen 30-by-20 feature windows and chronological dates. The primary experiment changes only the label to `delta[t+1] = P[t+1] - P[t]`, then reconstructs `P_hat[t+1] = P[t] + delta_hat[t+1]`. It runs on all five daily assets, retaining the negative oil observation. A separate simple-return experiment uses `r[t+1] = P[t+1]/P[t] - 1` and reconstructs `P_hat[t+1] = P[t] * (1 + r_hat[t+1])` on the four strictly positive daily series. Oil returns are excluded by protocol, with no filtering or clipping of its change experiment. Features still include levels: these experiments do not claim to make the entire input process stationary.

OLS retains training-only scaling/QR rank selection. RF tries 100 trees with depth 5 or 10 and leaf size 3. GBM tries 100 trees with (depth 2, rate .03) or (depth 3, rate .1). Validation RMSE in the **new target units** selects the candidate; return RMSE selection weights errors differently from price RMSE. LSTM uses the original 32 hidden units, dropout .1, Adam .001, gradient clipping 1, at most 60 epochs and patience 8, training-only target/input scalers, no shuffling and identical fixed seed 42. AMP is enabled only if its training-fixture loss check is finite and within 5% of FP32. CUDA/CPU choice, actual precision, batch/VRAM probes, best/last checkpoints, epoch histories, scaler cutoffs, candidates and CPU reload checks are saved for every job. Price predictions are not truncated to historical bounds and returns are not constrained to force plausible results.

Four explicit naive target forecasts are included: zero (exact persistence after reconstruction), training mean (fixed drift), the most recent observed change/return, and the training-majority sign times the training median nonzero magnitude. The latter's magnitude is an explicit forecast convention, not an optimized trading strategy. Last-observation forecasts use the prior label, already known at the current origin; they do not use the unknown current test label. Mean and majority baselines are fitted using training labels only. Zero/drift methods are standard benchmarks; see [Forecasting: Principles and Practice](https://otexts.com/fpp3/simple-methods.html).

### Fixed-split price-change experiment: reconstructed-price RMSE

| asset | OLS | RF | GBM | LSTM | Zero | Train mean | Last change/return | Train majority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | 4.571582 | 4.438386 | 5.312176 | 4.183376 | 4.189369 | 4.187791 | 5.667049 | 4.204890 |
| GOLD | 55.789309 | 58.994616 | 57.431033 | 47.329082 | 47.149802 | 47.104340 | 69.317525 | 46.752974 |
| NASDAQ | 311.695246 | 300.823462 | 308.417149 | 278.200766 | 278.421187 | 278.240905 | 415.059319 | 280.652295 |
| OIL | 1.691716 | 1.286918 | 1.283663 | 1.302453 | 1.282035 | 1.282647 | 1.797513 | 1.540960 |
| SP500 | 74.590237 | 68.805841 | 75.510545 | 65.767187 | 65.821692 | 65.782456 | 96.593267 | 66.816028 |

### Fixed-split simple-return experiment: reconstructed-price RMSE

| asset | OLS | RF | GBM | LSTM | Zero | Train mean | Last change/return | Train majority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | 5.681351 | 4.223403 | 4.200754 | 4.199022 | 4.189369 | 4.190219 | 5.739421 | 4.629594 |
| GOLD | 79.481707 | 59.948663 | 59.782107 | 47.407724 | 47.149802 | 47.040320 | 69.207539 | 47.863765 |
| NASDAQ | 383.360252 | 281.810327 | 286.843086 | 278.243324 | 278.421187 | 278.102451 | 418.663535 | 303.546302 |
| SP500 | 91.220563 | 65.366337 | 68.164187 | 65.787182 | 65.821692 | 65.764139 | 97.370915 | 71.489270 |

The OLS change-target forecasts should be almost identical to the original price-target forecasts: with an intercept and the current price in the feature span, subtracting current price from the label and adding it back at prediction is an algebraic reparameterization. A difference in RF/LSTM behavior is therefore informative about representation and model constraints, rather than evidence that changing a target guarantees new information.

The following post-training diagnostic compares LSTM target-prediction dispersion with actual target dispersion. Low reconstructed-price error can arise from forecasting near-zero changes, which is close to persistence, without accurately predicting the day's fluctuation. It must not be presented as evidence that the network recovered a strong return signal. Full amplitudes, means and sample correlations for all models are in `prediction_amplitudes.csv`; these are descriptive, not new selection criteria.

| asset | target | observed_target_std | predicted_target_std | predicted_to_observed_std |
| --- | --- | --- | --- | --- |
| AAPL | price_change | 4.187320 | 0.101543 | 0.024250 |
| GOLD | price_change | 46.743807 | 0.704494 | 0.015071 |
| NASDAQ | price_change | 278.024986 | 7.101890 | 0.025544 |
| OIL | price_change | 1.281202 | 0.157553 | 0.122973 |
| SP500 | price_change | 65.753270 | 1.559058 | 0.023711 |
| AAPL | simple_return | 0.019835 | 0.000909 | 0.045804 |
| GOLD | simple_return | 0.012919 | 0.000425 | 0.032932 |
| NASDAQ | simple_return | 0.015090 | 0.000611 | 0.040459 |
| SP500 | simple_return | 0.011594 | 0.000435 | 0.037527 |

### Walk-forward validation

Two assets (Apple and S&P 500) receive three expanding-history refits, covering the original 271 test observations in contiguous disjoint blocks of 91, 90 and 90. Before each block, the latest 270 available labels are validation and all earlier labels are training. Each fold refits preprocessing, candidate selection and all four models from scratch. The first fold uses the original training/validation boundaries; later folds can use earlier test labels only once they are available. Forecasts within each block continue to use the actual latest observed feature history; parameters remain frozen until the next block. This is block walk-forward one-step prediction, not a 90-step recursive forecast.

The LSTM walk-forward cap is 30 epochs with patience 8; other settings and tabular candidate budgets are unchanged. The largest actual walk-forward epoch count is 17, with every job's actual device, precision, batch, best epoch and fitted-label cutoff exported in `training_execution_summary.csv`. Validation continues to reserve a 270-observation tail, so these refits reduce staleness incrementally but do not implement daily training or final train-plus-validation refitting. The caps differ from the fixed-split experiment and should not be conflated with a pure refit-frequency causal test. Label availability is explicitly asserted under the daily after-close assumption; general temporal validation motivation is described in [scikit-learn's temporal-split documentation](https://scikit-learn.org/1.5/modules/generated/sklearn.model_selection.TimeSeriesSplit.html).

| asset | OLS | RF | GBM | LSTM | Zero | Train mean | Last change/return | Train majority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | 4.581473 | 4.392168 | 4.591877 | 4.201573 | 4.189369 | 4.187480 | 5.667049 | 4.205634 |
| SP500 | 74.020677 | 65.693874 | 70.378201 | 66.048960 | 65.821692 | 65.760008 | 96.593267 | 66.835769 |

| asset | model | rmse_ratio_vs_zero | mse_difference_ci_low | mse_difference_ci_high |
| --- | --- | --- | --- | --- |
| AAPL | LinearRegression | 1.093595 | 1.362857 | 5.712830 |
| AAPL | RandomForest | 1.048408 | 0.120221 | 3.283560 |
| AAPL | GradientBoosting | 1.096078 | 0.764372 | 6.155460 |
| AAPL | LSTM | 1.002913 | -0.110983 | 0.335870 |
| SP500 | LinearRegression | 1.124564 | 549.255238 | 1912.058749 |
| SP500 | RandomForest | 0.998058 | -354.251848 | 223.412524 |
| SP500 | GradientBoosting | 1.069225 | 197.784044 | 1116.648346 |
| SP500 | LSTM | 1.003453 | -28.894188 | 101.221380 |

### Directional accuracy and uncertainty

| asset | model | direction_accuracy | direction_coverage |
| --- | --- | --- | --- |
| AAPL | LinearRegression | 0.512915 | 1.000000 |
| AAPL | RandomForest | 0.457565 | 1.000000 |
| AAPL | GradientBoosting | 0.461255 | 1.000000 |
| AAPL | LSTM | 0.523985 | 1.000000 |
| AAPL | TrainMajorityDirectionMedianMagnitude | 0.538745 | 1.000000 |
| GOLD | LinearRegression | 0.457565 | 1.000000 |
| GOLD | RandomForest | 0.413284 | 1.000000 |
| GOLD | GradientBoosting | 0.416974 | 1.000000 |
| GOLD | LSTM | 0.428044 | 1.000000 |
| GOLD | TrainMajorityDirectionMedianMagnitude | 0.583026 | 1.000000 |
| NASDAQ | LinearRegression | 0.512915 | 1.000000 |
| NASDAQ | RandomForest | 0.435424 | 1.000000 |
| NASDAQ | GradientBoosting | 0.439114 | 1.000000 |
| NASDAQ | LSTM | 0.579336 | 1.000000 |
| NASDAQ | TrainMajorityDirectionMedianMagnitude | 0.571956 | 1.000000 |
| OIL | LinearRegression | 0.505535 | 1.000000 |
| OIL | RandomForest | 0.516605 | 1.000000 |
| OIL | GradientBoosting | 0.501845 | 1.000000 |
| OIL | LSTM | 0.523985 | 1.000000 |
| OIL | TrainMajorityDirectionMedianMagnitude | 0.494465 | 1.000000 |
| SP500 | LinearRegression | 0.531365 | 1.000000 |
| SP500 | RandomForest | 0.435424 | 1.000000 |
| SP500 | GradientBoosting | 0.424354 | 1.000000 |
| SP500 | LSTM | 0.553506 | 1.000000 |
| SP500 | TrainMajorityDirectionMedianMagnitude | 0.564576 | 1.000000 |

Directional accuracy compares three-way signs of predicted and observed price change. Nonzero coverage and accuracy conditional on an active forecast are also saved. Zero-change forecasts have 0% active coverage; their three-way score counts only exactly flat outcomes. They are **not a 0%-skill trading classifier**. Binary up/not-up accuracy is provided separately with zero mapped to not-up. Training-majority direction is the appropriate simple active comparator; 50% is not an assumed empirical baseline. Direction scores do not include trading costs, calibration or profitability.

| asset | target | rmse_ratio_vs_zero | mse_difference_vs_zero | mse_difference_ci_low | mse_difference_ci_high |
| --- | --- | --- | --- | --- | --- |
| AAPL | price_change | 0.998570 | -0.050174 | -0.259960 | 0.169716 |
| GOLD | price_change | 1.003802 | 16.938150 | -0.420881 | 35.910691 |
| NASDAQ | price_change | 0.999208 | -122.690820 | -885.458421 | 651.412901 |
| OIL | price_change | 1.015926 | 0.052769 | 0.004503 | 0.107122 |
| SP500 | price_change | 0.999172 | -7.172180 | -44.616935 | 36.146608 |
| AAPL | simple_return | 1.002304 | 0.080979 | -0.371257 | 0.551078 |
| GOLD | simple_return | 1.005470 | 24.388483 | -8.568872 | 59.072340 |
| NASDAQ | simple_return | 0.999361 | -99.010139 | -1323.470547 | 1260.285076 |
| SP500 | simple_return | 0.999476 | -4.541778 | -68.885687 | 72.969835 |

Each interval is a paired circular block bootstrap of daily `model squared price error - zero squared price error`, using block length 10, 2,000 resamples and seed 42. Negative differences favor the model. Price RMSE ratios below 1 occur in 6 of the 36 learned-model/target/asset comparisons; 0 have an unadjusted interval entirely below zero. Intervals are exploratory, use one prespecified block length, do not include training uncertainty, and have no multiple-comparison correction. Nominal coverage depends on the blocks adequately representing serial dependence; nonstationarity and fold-dependent models can weaken that approximation. Marginal wins or intervals overlapping zero cannot establish reliable superiority. Cross-asset dependence and the shared test period also prevent treating these comparisons as independent replications.

All MAE, RMSE, MAPE, R², direction/coverage, target-unit errors and bootstrap details are in `new_metrics.csv/json`. Price MAPE uses nonzero actual prices with zero counts recorded; target MAPE is also exported for transparency, but near-zero returns/changes make it unstable and it is not a selection criterion. Price R² can remain very high for persistence because the level varies slowly; target R² and error relative to zero change are more informative about incremental forecast skill. No returns, price errors or metrics are pooled across incompatible asset units.


## Verification and preservation

Executed 15 additional training jobs, each containing four learned models and four naive baselines. Independently reloaded every learned model on CPU and replayed all 23,848 saved forecast rows; all 88 aggregate metric records were recomputed from serialized predictions. Each job has hashes for its models, best/last checkpoints, histories, labels, splits and outputs. One AAPL change-target LSTM was retrained independently: all epoch training/validation losses and all 271 test predictions were bitwise identical on this machine. That is a same-environment reproducibility check, not a multi-seed robustness study.

An initial replay check used a fixed absolute tolerance across target units and failed for two near-zero Nasdaq change predictions. The maximum CPU/CUDA difference was 0.0000076294 index points. Diagnosis then replayed every LSTM on the original CUDA device: all 15 jobs' predictions matched their saved values **bitwise**. CPU differences were at most 0.0000000662 training-target standard deviations, below one FP32 machine epsilon at unit scale. CPU replay now uses an absolute bound of eight FP32 epsilons times the training target standard deviation, with zero relative tolerance; sklearn/baseline replay uses 1e-9 absolute/relative tolerance. This precision-aware verification change does not alter a model or empirical result. The initial failed log and all cross-device measurements remain in `replay_and_preservation.log` and `cross_device_diagnostics.json/log`.

A second verification attempt exposed a distinct, minor arithmetic effect: the LSTM target predictions are native FP32, so NumPy computes `1 + predicted_return` in FP32 before multiplying by the FP64 origin price. Exact replay must preserve that native dtype; casting the saved return to FP64 first produces slightly different implied prices. The failed attempt is retained in `replay_and_preservation_verified.log`; the successful full check is in `replay_and_preservation_final.log`. Both as-executed new result files remain untouched. A separate sensitivity calculation reconstructs **all** saved targets in FP64, without retraining, and saves `float64_reconstructed_predictions.csv`, `float64_reconstructed_metrics.csv` and provenance. Material differences are confined to these four LSTM return jobs:

| asset | model | max_price_difference | as_executed_rmse | float64_rmse | rmse_difference | direction_predictions_changed |
| --- | --- | --- | --- | --- | --- | --- |
| AAPL | LSTM | 0.000017 | 4.199022 | 4.199023 | 0.000001 | 0 |
| GOLD | LSTM | 0.000189 | 47.407724 | 47.407721 | -0.000003 | 0 |
| NASDAQ | LSTM | 0.001394 | 278.243324 | 278.243245 | -0.000079 | 0 |
| SP500 | LSTM | 0.000390 | 65.787182 | 65.787184 | 0.000002 | 0 |

The largest price-rounding difference is about 0.001394 Nasdaq index points; the largest absolute RMSE difference is about 0.000079 points. No directional predictions change. These are separately labeled numerical sensitivity results, not replacements for the as-executed tables above, and they do not establish learned-model superiority.

The complete automated suite executed 34 tests, with 0 failures, 0 errors and 0 skips. New boundary tests cover return reconstruction/scaling, rejection of negative-price returns, known-label naive forecasts, disjoint walk-forward blocks and directional abstention. Logs and JUnit XML are isolated in this validation directory. See `verification.json`, `tests_final.xml`, `tests_final.log` and `determinism_replication/verification.json`.

All 3,351 files in the pre-review preservation inventory retained their byte counts and SHA256 hashes. This includes the original run and checkpoints, previous result/verification files, input snapshots, thesis, existing source/configuration and verified offline defense package. The original defense ZIP SHA256 remains `99e58886fe9402b2de4b5f51cecdae66c690a4f39e322ed81f883ed96df64a92`. No original result or package was overwritten; this validation is an additive supplement.

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
