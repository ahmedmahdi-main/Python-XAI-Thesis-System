# Newly computed results: full_20261021T040901084647Z

Provenance: NEWLY_COMPUTED. Historical Table 4 is separately stored as THESIS_REPORTED_NOT_REPRODUCED. No survey responses were generated.

## AAPL

Units: USD per adjusted share; frequency: daily; test labels: 2024-12-02 to 2025-12-31 (n=271).

| Model | MAE | RMSE | MAPE % | R2 | Direction accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| LinearRegression | 3.30074 | 4.57158 | 1.46878 | 0.968764 | 0.512915 |
| RandomForest | 45.3372 | 51.404 | 18.5901 | -2.94923 | 0.461255 |
| GradientBoosting | 45.9575 | 52.5481 | 18.8 | -3.12699 | 0.461255 |
| LSTM | 57.5303 | 61.4149 | 24.1021 | -4.63723 | 0.461255 |
| Persistence | 2.78066 | 4.18937 | 1.2432 | 0.973769 | 0 |

## SP500

Units: index points; frequency: daily; test labels: 2024-12-02 to 2025-12-31 (n=271).

| Model | MAE | RMSE | MAPE % | R2 | Direction accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| LinearRegression | 51.8237 | 74.5902 | 0.861474 | 0.97217 | 0.531365 |
| RandomForest | 1475.77 | 1542.69 | 23.3894 | -10.9046 | 0.435424 |
| GradientBoosting | 1506.93 | 1570.28 | 23.9042 | -11.3342 | 0.435424 |
| LSTM | 916.748 | 980.47 | 14.4601 | -3.80868 | 0.435424 |
| Persistence | 43.5493 | 65.8217 | 0.725104 | 0.978328 | 0 |

## NASDAQ

Units: index points; frequency: daily; test labels: 2024-12-02 to 2025-12-31 (n=271).

| Model | MAE | RMSE | MAPE % | R2 | Direction accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| LinearRegression | 226.255 | 311.695 | 1.1447 | 0.97728 | 0.512915 |
| RandomForest | 4686.82 | 5117.83 | 22.1155 | -5.12521 | 0.435424 |
| GradientBoosting | 4780.19 | 5202.73 | 22.5777 | -5.33012 | 0.431734 |
| LSTM | 3224.27 | 3597.9 | 15.1472 | -2.02724 | 0.428044 |
| Persistence | 193.166 | 278.421 | 0.98099 | 0.981872 | 0 |

## GOLD

Units: USD per troy ounce (continuous futures proxy); frequency: daily; test labels: 2024-12-04 to 2025-12-31 (n=271).

| Model | MAE | RMSE | MAPE % | R2 | Direction accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| LinearRegression | 42.9903 | 55.7893 | 1.2398 | 0.988126 | 0.457565 |
| RandomForest | 1396.51 | 1487.18 | 39.6406 | -7.43748 | 0.413284 |
| GradientBoosting | 1405.12 | 1495.32 | 39.8984 | -7.53011 | 0.413284 |
| LSTM | 1214.83 | 1315.52 | 34.2253 | -5.60209 | 0.413284 |
| Persistence | 33.4347 | 47.1498 | 0.965323 | 0.991519 | 0.00369004 |

## OIL

Units: USD per barrel (continuous futures proxy); frequency: daily; test labels: 2024-12-04 to 2025-12-31 (n=271).

| Model | MAE | RMSE | MAPE % | R2 | Direction accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| LinearRegression | 1.27606 | 1.69172 | 1.95847 | 0.896577 | 0.505535 |
| RandomForest | 0.984922 | 1.32471 | 1.50786 | 0.936583 | 0.505535 |
| GradientBoosting | 1.01669 | 1.3823 | 1.56221 | 0.930949 | 0.509225 |
| LSTM | 1.03357 | 1.38363 | 1.59139 | 0.930816 | 0.476015 |
| Persistence | 0.944428 | 1.28203 | 1.4488 | 0.940603 | 0.00369004 |

## HOUSING

Units: index (January 2000=100); frequency: monthly; test labels: 2022-06-01 to 2025-12-01 (n=43).

| Model | MAE | RMSE | MAPE % | R2 | Direction accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| LinearRegression | 0.915075 | 1.15877 | 0.294386 | 0.990641 | 0.860465 |
| RandomForest | 113.525 | 114.184 | 35.8641 | -89.8772 | 0.488372 |
| GradientBoosting | 112.134 | 112.781 | 35.425 | -87.6575 | 0.488372 |
| LSTM | 99.0626 | 99.5576 | 31.3055 | -68.0862 | 0.488372 |
| Persistence | 1.6127 | 2.0182 | 0.517782 | 0.97161 | 0 |

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
