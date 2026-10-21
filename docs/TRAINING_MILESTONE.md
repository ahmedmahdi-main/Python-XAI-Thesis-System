# Day 1/2 executed milestone: source, data and forecasting

Run ID: full_20261021T040901084647Z. All six datasets have all four trained models plus persistence. CUDA BF16, batch64 verified in per-asset training.json. See per-model predictions/metrics and reload_check.json. Explanation/report/offline gates remain in progress.

| Asset | Observations | Test labels | OLS RMSE | RF RMSE | GBM RMSE | LSTM RMSE | Persistence RMSE |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| AAPL | 2766 | 2024-12-02 to 2025-12-31 | 4.571582 | 51.403976 | 52.548104 | 61.414866 | 4.189369 |
| SP500 | 2766 | 2024-12-02 to 2025-12-31 | 74.590237 | 1542.689376 | 1570.281033 | 980.470201 | 65.821692 |
| NASDAQ | 2766 | 2024-12-02 to 2025-12-31 | 311.695246 | 5117.832703 | 5202.730176 | 3597.900440 | 278.421187 |
| GOLD | 2766 | 2024-12-04 to 2025-12-31 | 55.789309 | 1487.179158 | 1495.319590 | 1315.520559 | 47.149802 |
| OIL | 2766 | 2024-12-04 to 2025-12-31 | 1.691716 | 1.324714 | 1.382298 | 1.383632 | 1.282035 |
| HOUSING | 468 | 2022-06-01 to 2025-12-01 | 1.158773 | 114.184249 | 112.781128 | 99.557614 | 2.018202 |

Models are newly computed, not reproduced historical Table4. Units differ by asset; errors must not be pooled. Housing is a retrospective revised-index experiment. All values above were read from actual computed metric files.

Implemented modules: source traceability; config/seed/storage; data sources/validation/features/windows/split/scaling; sklearn/PyTorch models; original-unit metrics/regimes; train/save/reload pipeline. Tests: 26 passed at the last full-suite run, plus missing-dashboard-artifact test passed separately. Known upstream deprecation warnings retained. Next priority: complete all SHAP/LIME exports, reports, fresh full tests, clean offline UI/model audit and defense package.
