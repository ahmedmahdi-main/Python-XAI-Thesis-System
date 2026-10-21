# Ten-minute offline defense

Before the session: use Windows CPython 3.12 AMD64, verify the package manifest, run offline installation, execute offline_smoke.py and verify_artifacts.py, and open the dashboard at 127.0.0.1:8501. Keep the static RESULTS.md and plots folder open as a presentation fallback. All snapshots/models/charts are local. Never start a new training run during the defense.

0:00-1:00 Overview: explain the end-of-close next-observed-close task and why a model needs auditable evidence. State that this is a reconstruction with newly computed results, not a claimed exact repetition of Table 4.

1:00-2:00 Data: select AAPL, show provider/range/hash and feature cutoff versus target dates. Explain adjustment/vintage limitations and why no target interpolation is allowed. Show 80/10/10 dates and the training-only transform boundary.

2:00-3:30 Compare models: four required models plus persistence on identical windows/dates. Discuss MAE/RMSE in dollars versus dimensionless R2/direction accuracy. Report the observed winners, including persistence, without promising LSTM superiority or investment returns.

3:30-5:30 Explain predictions: choose one saved test date/model. Read the SHAP baseline, forecast and signed contributions. Show the global ranking and feature-time heatmap (clearly labeled first observation). Read the LIME surrogate prediction/error and neighborhood R2 for the SAME selected date. Explain that post-hoc attribution leaves the fitted forecast unchanged and does not prove causality.

5:30-6:30 Regimes: show trailing-20-observation thresholds and group counts. Discuss descriptive errors without inventing absent market cases or claiming significance from small groups.

6:30-7:15 Monthly housing: show that only a monthly index is used, no fictitious OHLCV. Revised observation dates do not imply real-time publication availability; results are a separate retrospective experiment with different units.

7:15-8:15 Thesis alignment: show Table 4 as historical, with unavailable original units/data, separately from new results. Explain the appendix's ether.csv/DecisionTree/XGBoost/80-20 discrepancy and corrected imputation/forecast-target protocol.

8:15-9:00 Survey: explicitly state that the text contains 78/85/70 but raw responses and participant count are unavailable. No new participants or trust improvement have been fabricated.

9:00-10:00 Reproducibility: show run configuration, CUDA/CPU metadata, fixed seeds, actual tests, snapshot hashes, checkpoint/reload evidence and exported report. Open a local PNG/SVG or standalone forecast HTML to demonstrate the fallback. State that separate-media backup must be copied/verified before travel; a same-disk ZIP is not independent disaster recovery.
