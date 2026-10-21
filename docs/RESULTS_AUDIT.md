# Results and provenance audit

Run: `full_20261021T040901084647Z`; NEWLY_COMPUTED. Source DOCX SHA256 `a279ce433768fe7ecbf12d191a29d547874904e143e0141810a20b752c49f866`. All source/lock hashes recorded in run.json were independently checked against the final files.

| Claim | Evidence | Classification | Status |
| --- | --- | --- | --- |
| Four trained models on six datasets | artifacts/runs/full_20261021T040901084647Z/<asset>/training.json, model files, predictions.csv and metrics.json | Newly computed; original units per asset | Executed and independently CPU-reloaded |
| Accurate source/label alignment and metrics | artifacts/runs/full_20261021T040901084647Z/verification.json | Snapshot-backed recomputation, common model dates | Passed for all six assets |
| SHAP/LIME paired explanations | artifacts/runs/full_20261021T040901084647Z/<asset>/<model>/explanations/ | 240 held-out model/observation pairs, 24 model/asset bundles; training-only background | Generated and checked |
| Automated tests | artifacts/tests/final.xml and final.log | 27 tests, zero failures/errors/skips; 923 upstream deprecation warnings | Executed |
| Clean offline environment | artifacts/tests/clean_environment.json, offline_dashboard.json, offline_models.log | 89 locked dependencies and project wheel installed --no-index; system-site packages disabled | Dashboard and all CPU model reload audits passed |
| Historical Table 4 | docs/thesis_reported_reference.json; Ch4 4.2/P1026-P1049 | THESIS_REPORTED_NOT_REPRODUCED; dataset/units unspecified | Text verified, empirical replication unavailable |
| Historical 78/85/70 survey | docs/SURVEY_EVIDENCE_STATUS.md; Ch4 4.3/P1053-P1059 | Historical claims; N/raw responses unavailable | No fabricated records, no new human study |
| Backup on separate media/cloud | Local package/ZIP only | Same disk; external transfer not verified | Requires a real external copy before travel |

## Dataset snapshots

| Asset / symbol | Frequency / units | Observations and dates | SHA256 |
| --- | --- | --- | --- |
| AAPL / AAPL | daily / USD per adjusted share | 2766: 2015-01-02 to 2025-12-31 | 87e5bef4aec197b26bd182f3ee796c9c19b91ec8f50ceb70ee9d0fb89ab64755 |
| SP500 / ^GSPC | daily / index points | 2766: 2015-01-02 to 2025-12-31 | c10fcd903ed9e96d29b554b0848a446be1995ecd671a2ef3a4536737d0b2ba1d |
| NASDAQ / ^IXIC | daily / index points | 2766: 2015-01-02 to 2025-12-31 | 3fb57868cff90c6fc494b339fac3fd319e8463e39ba150092f5fcf1f5883faf1 |
| GOLD / GC=F | daily / USD per troy ounce (continuous futures proxy) | 2766: 2015-01-02 to 2025-12-31 | e12ffae8fcdd2c903f0449085f3bfeb2979247169817c2d745127ce153d2ddf1 |
| OIL / CL=F | daily / USD per barrel (continuous futures proxy) | 2766: 2015-01-02 to 2025-12-31 | 2776e2290dcf9b2c9ea58adee99541f13039439106ee34c78bf5ccccf9fdb1bc |
| HOUSING / CSUSHPINSA | monthly / index (January 2000=100) | 468: 1987-01-01 to 2025-12-01 | a92e44e17dde0464bb82ab7f2621425b07adea1267f2da2d9f2870fa4addd3b6 |

## Actual model errors

Full MAE/RMSE/MAPE/R2/direction tables, split dates, runtime and limitations are in docs/RECONSTRUCTED_RESULTS.md and this run's summary.json. No raw MAE is averaged across assets. Persistence has the lowest RMSE for all five daily assets. OLS leads monthly housing, a retrospective revised-index experiment, not a publication-time forecast.

## Explanation interpretation

SHAP additivity does not validate predictive skill or causality. LIME has substantial measured local approximation error in several high-dimensional/correlated cases; the dashboard exposes the actual errors and neighborhood fit rather than claiming trust. Fixed-subset/one-cycle permutation approximations and seeded stability checks are explicitly limited.

## Source and numerical discrepancies

The narrative four-model/80-10-10 framework differs from appendix ether.csv/DecisionTree/XGBoost/80-20 screenshots. The missing CSV and raw survey are not invented. Initial cuDNN batch-probe, OLS conditioning and parallel-inference numerical failures were reproduced and fixed; superseded runs are preserved. Final outputs come from real runs. Source TOC page references are verified as TOC entries; physical pagination remains unverified.

## Offline defense

Dashboard: http://127.0.0.1:8501. Launch using scripts/launch_demo.py in the installed environment. Portable single command: python scripts/offline_demo.py after entering defense_package, with Windows CPython3.12 installed. The Python installer is not bundled. Static PNG/SVG/HTML and RESULTS.md are available as presentation fallback.


Final packaging evidence: artifacts/tests/package_verification.json. All 1,459 bundled files matched PACKAGE_MANIFEST after relocation. ZIP CRC and SHA256 verified; local backup: backups/defense_full_20261021T040901084647Z.zip. SHA256: 99e58886fe9402b2de4b5f51cecdae66c690a4f39e322ed81f883ed96df64a92. Independent second-medium/cloud backup is still not verified.
