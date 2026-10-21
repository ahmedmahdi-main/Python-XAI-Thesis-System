# Newly computed results: quick_cpu_20261021T042222183460Z

Provenance: NEWLY_COMPUTED. Historical Table 4 is separately stored as THESIS_REPORTED_NOT_REPRODUCED. No survey responses were generated.

## AAPL

Units: USD per adjusted share; frequency: daily; test labels: 2024-12-02 to 2025-12-31 (n=271).

| Model | MAE | RMSE | MAPE % | R2 | Direction accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| LinearRegression | 3.30074 | 4.57158 | 1.46878 | 0.968764 | 0.512915 |
| RandomForest | 45.5592 | 51.6615 | 18.6805 | -2.9889 | 0.461255 |
| GradientBoosting | 56.461 | 62.0538 | 23.3575 | -4.75513 | 0.461255 |
| LSTM | 34.5803 | 39.235 | 14.2358 | -1.30073 | 0.461255 |
| Persistence | 2.78066 | 4.18937 | 1.2432 | 0.973769 | 0 |

## SP500

Units: index points; frequency: daily; test labels: 2024-12-02 to 2025-12-31 (n=271).

| Model | MAE | RMSE | MAPE % | R2 | Direction accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| LinearRegression | 51.8237 | 74.5902 | 0.861474 | 0.97217 | 0.531365 |
| RandomForest | 1502.55 | 1567.63 | 23.8268 | -11.2926 | 0.435424 |
| GradientBoosting | 1687.12 | 1745.36 | 26.819 | -14.238 | 0.435424 |
| LSTM | 1308.36 | 1359.11 | 20.7833 | -8.23991 | 0.435424 |
| Persistence | 43.5493 | 65.8217 | 0.725104 | 0.978328 | 0 |

## Scientific limits

- Reconstruction, not exact replication: thesis omits instrument/date/sample/units and narrative hyperparameters; appendix implements different models and split.
- Retrospectively adjusted/revised provider snapshots are not point-in-time historical vintages.
- House-price experiment is monthly, retrospective next-observation regression, not publication-time forecasting or daily trading.
- All four models use identical full windows; flattening increases collinearity and dimensionality for tabular models.
- High price-level R2 does not establish trading skill. Compare with persistence and directional accuracy; no transaction-cost backtest or investment-return claim.
- Bounded SHAP subset and permutation budgets are approximate; correlated-feature marginal masking and LIME neighborhoods may be off-manifold. Attributions are not causal.
- Explanation seed stability is a bounded numerical check, not proof of market robustness or human trust.
- Historical survey claims have no participant count/raw responses; no new human study was conducted.
- Seeded deterministic settings improve repeatability; cross-version/hardware bitwise equality is not guaranteed. Runtime batch probing may choose a different batch on another machine.
- Held-out results are descriptive for one fixed chronological split; no claim of universal model superiority or statistical significance.
