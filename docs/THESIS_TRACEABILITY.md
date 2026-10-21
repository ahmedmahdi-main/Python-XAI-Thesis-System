# Verified thesis traceability

Source: docs/original_thesis.docx, Mohammad Saleh, Damghan University, Dr. Sajad Rahmani. SHA256: a279ce433768fe7ecbf12d191a29d547874904e143e0141810a20b752c49f866. Uploaded generated filename copied unchanged to the canonical path.

All 1,310 paragraphs (including table cells, glossaries, references and appendix), all 15 media files and document relationships were inspected. Stable text anchors P0001-P1310 are in source_extract.txt/json. Images are preserved in source_media/. No executable code files or datasets are embedded in word/embeddings. The appendix DOES contain code screenshots, described below.

Page references below are verified against the document's own TOC (P0088-P0116), NOT independently rendered pagination. DOCX has no docProps/app.xml and no reliable rendered-page boundaries. The TOC is internally inconsistent: Chapter 4 p74, introduction p65, then later sections p82 onward. Section and paragraph anchors are reliable; physical page numbers remain unverified.

| Requirement / short source anchor | Verified chapter/section and paragraph | TOC page | Intended module | Acceptance evidence | Specificity/status |
| --- | --- | --- | --- | --- | --- |
| Mixed quantitative and qualitative design | Ch4 3.1, P0952-P0958 | 88 | pipelines/train.py; survey evidence status | Computed metrics; no invented participants | Verified design; survey not reproducible |
| Yahoo Finance / Quandl / government sources | Ch4 3.2, P0960-P0961 | 90 | io/data_sources.py | Actual snapshot hashes and manifests | Providers given; exact symbols/dates absent |
| MA/EMA/RSI/MACD/Bollinger and normalization | Ch4 3.2, P0963-P0969 | 90 | data/features.py; data/preprocess.py | Causality and train-only scaling tests | Indicator names exact; parameters absent |
| Chronological order / leakage prevention | Ch4 3.2, P0967/P0969 | 90 | data/split.py; data/windows.py | Label boundaries and future mutation tests | Exact requirement |
| S&P500/NASDAQ/equities, commodities, real estate | Ch4 3.3, P0971-P0981 | 91 | configs/datasets.yaml | Per-asset/frequency artifacts | Categories given; sample sizes/dates absent |
| Linear Regression, RF, LSTM, GBM | Ch4 3.4, P0982-P0992 | 93 | models/sklearn_models.py; lstm_model.py | Four models on common dates | Exact model families; configuration absent |
| SHAP/LIME; summary/waterfall/force/dependence | Ch4 3.5, P0993-P1002 | 94 | explain/ and reports/ | Real exports; additivity and fidelity | Methods exact; background/budgets absent |
| MAE/RMSE/MAPE/R2 and stability/quality | Ch4 3.6, P1003-P1009 | 96 | evaluate/metrics.py; explain/quality.py | Original-unit metrics; measured stability | Human trust remains separate |
| Python/sklearn/TensorFlow/Keras; 80/10/10 | Ch4 4.1, P1018-P1025 | 99 | config.py; seed.py; train.py | Split/config/environment manifests | Exact ratio; PyTorch is explicit user override |
| Fixed seed, Adam, early stopping, tuning | Ch4 4.1, P1020-P1022 | 99 | models/; seed.py | Saved actual training configurations | Numeric seed/epochs/batch/layers absent in narrative |
| Table 4 LR 1.23/1.67/.65; RF .85/1.10/.80; LSTM .76/1.02/.85; GBM .82/1.05/.82 | Ch4 4.2, P1026-P1049; image9 at P1050 | 101 | docs/thesis_reported_reference.json | Historical/computed provenance separation | Text/figure verified; units/dataset absent |
| Survey 78%, 85%, 70% | Ch4 4.3, P1053-P1059 | 102 | SURVEY_EVIDENCE_STATUS.md | Historical labels only | Claims in text; N/raw responses/protocol absent |
| Bull/bear/stable cases | Ch4 4.4, P1060-P1065 | 103 | evaluate/regimes.py | Trailing-return regime counts/errors | Thresholds/dates absent; winners not assumed |
| Computational overhead and conflicting explanations | Ch4 5.3, P1091-P1098 | 109 | explain/quality.py | Runtime and measured agreement | Qualitative requirement |
| Appendix screenshots | P1284/P1285/P1290, images13/11/12/14/15 | 121 | Audit only; not copied into forecasting pipeline | Scientific discrepancy log | Different models/task; missing ether.csv |

## Appendix discrepancy - critical

image13.png at P1284 imports DecisionTreeRegressor and XGBRegressor, reads `ether.csv` with delimiter comma, sets `X = data.iloc[:, 1:-1]` and `y = data['Close']`, coerces numeric fields and imputes X/y with full-data means before any split. CSV is absent, so whether Close also lies in X cannot be established. There is no visible next-step target shift.

image11.png at P1284 uses train_test_split(test_size=0.2, random_state=42, shuffle=False), DecisionTree max_depth=5, XGBoost n_estimators=100/max_depth=6/learning_rate=.1/seed42. It has no validation set or LSTM. image12 evaluates these two models with MAE/MSE/RMSE/R2; images14/15 plot and compare them. These screenshots do not implement the narrative's four models, 80/10/10 protocol, SHAP or LIME. Full-data imputation leaks future distribution information. Contemporaneous Close regression is not evidence of next-day forecasting skill. The reconstruction corrects these issues explicitly and never labels its new results exact reproductions.

Other figures: image6 at P0514 prints R2 bars 7824/9016 and RMSE 557/374 without clear scaling; image8 at P0518 has large feature bars with unclear units. They cannot serve as verified empirical metrics. The Chapter 4 figure image9 matches Table 4 but combines unitful errors and dimensionless R2 on one axis; new charts separate metrics. Ch3 P0732 says 2,022 papers while P0847 prints 2025; Ch2 describes a different 6,086-to-30 review. These are literature-review discrepancies, not reconstructed observations.

No physical page numbers, unavailable survey records, ether.csv contents or historical training outputs are invented. See ASSUMPTIONS_AND_DEVIATIONS.md for chosen reconstruction defaults.
