# فهرس آلي أولي للشيفرة

يشمل main.py ومجلدات dashboard وsrc وscripts وtests. تستبعد نسخ artifacts المحفوظة ومخرجات البناء والبيئات. هذا جرد نحوي آلي وليس دليلاً على اكتمال الشرح. عدد الأسطر القابلة للتنفيذ تقريبي من أرقام أسطر bytecode وقد يتغير حسب إصدار Python. الأسطر ذات الرموز تحتسب بداية الرمز فقط ولا تكفي وحدها لإثبات التغطية.

| المسار | الأسطر الفعلية | تنفيذية تقريبية | الأصناف والدوال (الاسم:السطر) | الواردات |
|---|---:|---:|---|---|
| `main.py` | 11 | 5 | — | pathlib, runpy |
| `dashboard/app.py` | 209 | 173 | read_json:22, load_table:27, csv_table:31, saved_image:35, overview:42, preprocessing:54, forecasting:70, comparison:85, explanations:95, regimes:127, reproducibility:137, thesis_alignment:162, main:179 | json, numpy, pandas, pathlib, plotly.express, plotly.graph_objects, streamlit |
| `scripts/audit_reconstruction_precision.py` | 37 | 31 | main:13 | argparse, numpy, pandas, pathlib, xai_finance.storage, xai_finance.validation.design, xai_finance.validation.statistics |
| `scripts/bootstrap_cpu.py` | 23 | 21 | — | os, pathlib, subprocess, sys |
| `scripts/browser_smoke_cpu.py` | 118 | 101 | CDP:19, __init__:20, call:25, evaluate:38, main:45 | argparse, base64, json, pathlib, subprocess, time, urllib.request, websockets.sync.client |
| `scripts/build_validation_report.py` | 28 | 23 | main:10 | argparse, base64, html, pathlib, xai_finance.storage, xai_finance.validation.report |
| `scripts/check_dashboard_cpu.py` | 64 | 53 | main:13, check:20, connect:24, connect_ex:28 | argparse, json, pathlib, socket, streamlit.testing.v1 |
| `scripts/demo_wizard.py` | 350 | 298 | say:30, environment:37, run:42, sha256:51, verify_manifest:59, verify_artifacts:74, runtime_check:96, process_stamp:101, owned_state:124, terminate_owned_tree:134, Entry:139, healthy:175, launch_lock:184, start:202, stop:253, setup:275, main:315 | argparse, contextlib, ctypes, datetime, hashlib, json, msvcrt, os, pathlib, platform, signal, socket, struct, subprocess, sys, time, urllib.request, venv, webbrowser |
| `scripts/diagnose_validation_replay.py` | 38 | 32 | main:15 | argparse, joblib, numpy, pandas, pathlib, xai_finance.models.lstm_model, xai_finance.pipelines.train, xai_finance.seed, xai_finance.storage |
| `scripts/download_data.py` | 4 | 3 | — | xai_finance.config, xai_finance.io.data_sources |
| `scripts/generate_defense_package.py` | 54 | 45 | copy_project:11, archive_package:24, main:39 | pathlib, shutil, xai_finance.config, xai_finance.pipelines.train, xai_finance.storage, zipfile |
| `scripts/launch_demo.py` | 8 | 7 | — | os, pathlib, subprocess, sys |
| `scripts/offline_demo.py` | 9 | 8 | — | pathlib, subprocess, sys |
| `scripts/offline_guard/sitecustomize.py` | 32 | 25 | _check:12, connect:16, connect_ex:21, getaddrinfo:26 | os, socket |
| `scripts/offline_smoke.py` | 38 | 31 | loopback_only:13 | json, pathlib, socket, streamlit.testing.v1 |
| `scripts/package_cpu_defense.py` | 97 | 87 | digest:14, main:19 | argparse, datetime, hashlib, json, pathlib, shutil, zipfile |
| `scripts/package_scientific_validation.py` | 79 | 64 | EmbeddedImages:16, __init__:17, handle_starttag:21, verify_offline_page:26, snapshot_source:39, package_addendum:50, main:69 | PIL, argparse, base64, hashlib, html.parser, pathlib, shutil, xai_finance.config, xai_finance.storage, zipfile |
| `scripts/replicate_validation_lstm.py` | 51 | 45 | main:17 | argparse, joblib, numpy, pathlib, threadpoolctl, xai_finance.config, xai_finance.models.lstm_model, xai_finance.pipelines.train, xai_finance.seed, xai_finance.storage, xai_finance.validation.design |
| `scripts/run_full.py` | 9 | 8 | — | os, pathlib, subprocess, sys |
| `scripts/run_quick.py` | 9 | 8 | — | os, pathlib, subprocess, sys |
| `scripts/run_scientific_validation.py` | 29 | 23 | main:11 | argparse, pathlib, xai_finance.config, xai_finance.storage, xai_finance.validation.audit, xai_finance.validation.experiments |
| `scripts/setup_offline.py` | 8 | 6 | — | pathlib, subprocess, sys |
| `scripts/start_scientific_validation.py` | 44 | 36 | protected_files:9, main:14 | datetime, pathlib, xai_finance.config, xai_finance.storage |
| `scripts/test_deployment_cpu.py` | 82 | 72 | main:15, batch:26 | argparse, importlib.util, json, os, pathlib, socket, subprocess, urllib.request |
| `scripts/verify_artifacts.py` | 75 | 63 | verify_asset:17, verify_explanation:42, main:59 | numpy, pandas, pathlib, xai_finance.config, xai_finance.io.data_sources, xai_finance.pipelines.report, xai_finance.pipelines.train, xai_finance.storage |
| `scripts/verify_cpu_replay.py` | 90 | 81 | main:18, connect:24 | argparse, importlib, json, numpy, os, pathlib, pkgutil, socket, sys, threadpoolctl, torch, verify_artifacts, verify_scientific_validation, xai_finance, xai_finance.explain.lime_explain, xai_finance.explain.shap_explain, xai_finance.pipelines.train, xai_finance.seed, xai_finance.storage |
| `scripts/verify_environment.py` | 3 | 2 | — | xai_finance.environment |
| `scripts/verify_preservation_cpu.py` | 31 | 23 | digest:11, main:16 | argparse, hashlib, json, pathlib |
| `scripts/verify_scientific_validation.py` | 93 | 78 | replay_job:18, verify_aggregate:49, preservation_receipt:66, main:77 | argparse, dataclasses, datetime, numpy, pandas, pathlib, xai_finance.config, xai_finance.pipelines.train, xai_finance.seed, xai_finance.storage, xai_finance.validation.design, xai_finance.validation.statistics |
| `src/xai_finance/__init__.py` | 3 | 2 | — | — |
| `src/xai_finance/cli.py` | 42 | 33 | main:9, execute:18 | argparse, os, xai_finance.config, xai_finance.environment, xai_finance.io.data_sources, xai_finance.pipelines.explain, xai_finance.pipelines.report, xai_finance.pipelines.train |
| `src/xai_finance/config.py` | 21 | 15 | project_root:5, load_config:16 | pathlib, yaml |
| `src/xai_finance/data/__init__.py` | 0 | 0 | — | — |
| `src/xai_finance/data/features.py` | 43 | 37 | relative_strength:5, features:14, return_features:35 | numpy, pandas |
| `src/xai_finance/data/preprocess.py` | 28 | 20 | TrainingScalers:10, transform_windows:16, inverse_target:20, fit_training_scalers:24 | dataclasses, numpy, sklearn.preprocessing, xai_finance.data.windows |
| `src/xai_finance/data/split.py` | 9 | 7 | chronological_indices:4 | numpy |
| `src/xai_finance/data/validate.py` | 28 | 24 | validate_prices:5, validate_ohlc:22 | numpy, pandas |
| `src/xai_finance/data/windows.py` | 37 | 28 | WindowDataset:10, flat:21, flat_names:25, build_windows:29 | dataclasses, numpy, pandas, xai_finance.data.split |
| `src/xai_finance/environment.py` | 24 | 20 | verify_environment:11 | json, torch, xai_finance.config, xai_finance.pipelines.train, xai_finance.seed, xai_finance.storage |
| `src/xai_finance/evaluate/__init__.py` | 0 | 0 | — | — |
| `src/xai_finance/evaluate/metrics.py` | 14 | 12 | forecast_metrics:5 | numpy, sklearn.metrics |
| `src/xai_finance/evaluate/regimes.py` | 15 | 10 | regime_labels:7, regime_metrics:11 | numpy, pandas, xai_finance.evaluate.metrics |
| `src/xai_finance/explain/__init__.py` | 0 | 0 | — | — |
| `src/xai_finance/explain/lime_explain.py` | 11 | 9 | explain_lime:5 | lime.lime_tabular, numpy |
| `src/xai_finance/explain/quality.py` | 17 | 13 | attribution_stability:5, lime_weight_vector:13 | numpy, scipy.stats |
| `src/xai_finance/explain/shap_explain.py` | 28 | 24 | explain_shap:5, shap_reconstruction:24 | numpy, shap |
| `src/xai_finance/io/__init__.py` | 0 | 0 | — | — |
| `src/xai_finance/io/data_sources.py` | 66 | 54 | yahoo_prices:13, fred_prices:23, download_asset:34, load_snapshot:52, download_all:64 | datetime, io, pandas, requests, xai_finance.config, xai_finance.data.validate, xai_finance.storage, yfinance |
| `src/xai_finance/models/__init__.py` | 0 | 0 | — | — |
| `src/xai_finance/models/baselines.py` | 5 | 3 | persistence:4 | numpy |
| `src/xai_finance/models/linear_preprocess.py` | 22 | 16 | IndependentColumns:6, __init__:9, fit:12, transform:21 | numpy, scipy.linalg, sklearn.base |
| `src/xai_finance/models/lstm_model.py` | 205 | 176 | PriceLSTM:16, __init__:17, forward:23, LSTMPredictor:29, predict:36, probe_precision:48, scaled_loss:68, batch_probe:75, measure_batch:100, train_epoch:117, checkpoint_state:136, optimize_epochs:140, fit_lstm:167, training_tensors:189, load_lstm:199 | copy, dataclasses, numpy, pathlib, time, torch, xai_finance.data.preprocess, xai_finance.data.windows, xai_finance.seed, xai_finance.storage |
| `src/xai_finance/models/sklearn_models.py` | 38 | 32 | candidates:14, fit_candidates:24 | numpy, sklearn.ensemble, sklearn.linear_model, sklearn.metrics, sklearn.pipeline, sklearn.preprocessing, time, xai_finance.data.windows, xai_finance.models.linear_preprocess |
| `src/xai_finance/pipelines/__init__.py` | 0 | 0 | — | — |
| `src/xai_finance/pipelines/explain.py` | 108 | 93 | fixed_subset:18, explain_experiment:22, explain_asset:35, explain_model:50, explain_local_dates:76, save_regime_drivers:98 | numpy, pandas, pathlib, threadpoolctl, time, torch, xai_finance.evaluate.regimes, xai_finance.explain.lime_explain, xai_finance.explain.quality, xai_finance.explain.shap_explain, xai_finance.pipelines.train, xai_finance.reports.plots, xai_finance.seed, xai_finance.storage |
| `src/xai_finance/pipelines/report.py` | 119 | 101 | generate_report:17, asset_report:33, verify_saved_metrics:52, extra_charts:61, export_coefficients:87, research_limitations:99, write_research_markdown:103, write_inventory:117 | datetime, matplotlib.pyplot, numpy, pandas, pathlib, plotly.express, shutil, xai_finance.config, xai_finance.evaluate.metrics, xai_finance.pipelines.train, xai_finance.reports.plots, xai_finance.storage |
| `src/xai_finance/pipelines/train.py` | 134 | 110 | software_environment:28, train_experiment:34, save_windows:52, load_windows:57, split_manifest:62, train_asset:66, evaluate_asset:89, load_models:110, verify_reload:117, save_next_forecasts:126, resolve_run:132 | datetime, importlib.metadata, joblib, numpy, os, pandas, pathlib, platform, shutil, subprocess, sys, threadpoolctl, xai_finance.config, xai_finance.data.features, xai_finance.data.windows, xai_finance.evaluate.metrics, xai_finance.evaluate.regimes, xai_finance.io.data_sources, xai_finance.models.baselines, xai_finance.models.lstm_model, xai_finance.models.sklearn_models, xai_finance.seed, xai_finance.storage |
| `src/xai_finance/reports/__init__.py` | 0 | 0 | — | — |
| `src/xai_finance/reports/plots.py` | 108 | 91 | save_figure:16, forecast_charts:24, metric_charts:39, loss_chart:49, research_flow:60, explanation_charts:75, aggregate_lag_charts:92 | matplotlib, matplotlib.pyplot, numpy, pandas, pathlib, shap |
| `src/xai_finance/seed.py` | 37 | 31 | seed_experiment:10, select_device:22 | numpy, os, random, torch |
| `src/xai_finance/storage.py` | 29 | 20 | sha256:8, json_default:13, write_json:23, read_json:28 | hashlib, json, numpy, pathlib |
| `src/xai_finance/validation/__init__.py` | 1 | 1 | — | — |
| `src/xai_finance/validation/audit.py` | 92 | 79 | causal_feature_check:14, alignment_check:22, scaler_check:33, distribution_shift:45, frozen_metric_check:64, audit_original:78 | joblib, numpy, pandas, xai_finance.data.features, xai_finance.data.preprocess, xai_finance.data.windows, xai_finance.evaluate.metrics, xai_finance.io.data_sources, xai_finance.pipelines.train, xai_finance.storage |
| `src/xai_finance/validation/design.py` | 54 | 42 | target_values:8, implied_prices:18, transformed_windows:26, walk_forward_partitions:30, naive_predictions:44 | dataclasses, numpy, xai_finance.data.windows |
| `src/xai_finance/validation/diagnostics.py` | 60 | 51 | target_distribution:11, lstm_output_bound:22, supplemental_audit:32, prediction_amplitudes:54 | joblib, numpy, pandas, torch, xai_finance.pipelines.train, xai_finance.storage, xai_finance.validation.statistics |
| `src/xai_finance/validation/experiments.py` | 102 | 88 | fit_models:20, predictions_table:31, job_configuration:42, experiment_job:49, run_experiments:78, aggregate_experiments:92 | dataclasses, gc, joblib, numpy, pandas, pathlib, threadpoolctl, torch, xai_finance.models.lstm_model, xai_finance.models.sklearn_models, xai_finance.pipelines.train, xai_finance.seed, xai_finance.storage, xai_finance.validation.design, xai_finance.validation.statistics |
| `src/xai_finance/validation/figures.py` | 127 | 108 | save_figure:18, frozen_forecasts:24, rmse_comparison:42, bootstrap_intervals:65, walk_forward_errors:82, directional_accuracy:100, generate_figures:116 | matplotlib, matplotlib.colors, matplotlib.pyplot, numpy, pandas, pathlib, xai_finance.storage |
| `src/xai_finance/validation/report.py` | 242 | 115 | markdown_table:12, rmse_table:21, dataset_table:28, execution_summary:36, evidence_tables:45, principal_findings:62, audit_narrative:72, experiment_narrative:100, write_report:163 | pandas, pathlib, xai_finance.config, xai_finance.storage, xai_finance.validation.diagnostics, xai_finance.validation.figures, xml.etree.ElementTree |
| `src/xai_finance/validation/statistics.py` | 31 | 24 | directional_statistics:6, paired_bootstrap:13, evaluation_metrics:23 | numpy, xai_finance.evaluate.metrics |
| `tests/conftest.py` | 19 | 13 | analytic_prices:10, window_fixture:18 | numpy, pandas, pytest, xai_finance.data.features, xai_finance.data.windows |
| `tests/test_dashboard.py` | 15 | 12 | test_missing_artifacts_shows_actionable_setup_commands:7 | pathlib, shutil, streamlit.testing.v1 |
| `tests/test_explain_consistency.py` | 30 | 25 | test_shap_additivity_and_posthoc_explanation_preserve_forecast:10, test_lime_accepts_batch_prediction_and_returns_measured_surrogate_error:22 | numpy, pytest, xai_finance.explain.lime_explain, xai_finance.explain.shap_explain, xai_finance.models.sklearn_models |
| `tests/test_lstm_training.py` | 28 | 22 | test_cuda_batch_probe_supports_cudnn_backward:10, test_cpu_lstm_training_checkpoint_and_inverse_scale_roundtrip:20 | numpy, pytest, torch, xai_finance.models.lstm_model, xai_finance.seed |
| `tests/test_metrics_and_models.py` | 54 | 40 | test_metrics_match_hand_computable_original_unit_errors:11, test_zero_target_mape_is_explicitly_undefined:20, test_persistence_uses_current_close_without_future_labels:27, test_repeated_forest_inference_is_bitwise_stable:32, test_regime_boundary_uses_declared_trailing_return_threshold:41, test_saved_tabular_model_preserves_predictions_without_refitting:46 | joblib, numpy, pytest, xai_finance.evaluate.metrics, xai_finance.evaluate.regimes, xai_finance.models.baselines, xai_finance.models.sklearn_models |
| `tests/test_provider_integration.py` | 22 | 18 | test_real_provider_ols_explanation_reconstructs_stably:12 | numpy, pytest, xai_finance.data.features, xai_finance.data.windows, xai_finance.explain.shap_explain, xai_finance.io.data_sources, xai_finance.models.sklearn_models |
| `tests/test_scientific_validation.py` | 60 | 48 | test_target_reconstruction_and_scaling_restore_next_price:12, test_return_protocol_rejects_negative_price_but_changes_preserve_it:22, test_walk_forward_blocks_are_disjoint_and_fit_only_available_labels:31, test_naive_predictions_do_not_use_unknown_test_labels:42, test_zero_prediction_is_directional_abstention:55 | dataclasses, numpy, pytest, xai_finance.data.preprocess, xai_finance.validation.design, xai_finance.validation.statistics |
| `tests/test_temporal_integrity.py` | 78 | 62 | test_future_price_mutation_preserves_past_features:13, test_targets_are_exactly_next_observed_close_and_windows_end_at_origin:23, test_split_targets_never_cross_partition_boundary:34, test_heldout_mutation_cannot_change_fitted_scalers:45, test_target_inverse_transform_restores_original_units:56, test_invalid_provider_snapshot_is_rejected:63, test_insufficient_history_fails_instead_of_empty_test_set:76 | numpy, pandas, pytest, xai_finance.data.features, xai_finance.data.preprocess, xai_finance.data.split, xai_finance.data.validate, xai_finance.data.windows |

المجموع: 77 ملفاً؛ 3929 سطراً فعلياً؛ 3181 سطراً تنفيذياً تقريبياً.

لا يستخرج هذا الجرد آلياً المسؤوليات أو نقاط الدخول أو الملفات المقروءة والمكتوبة؛ تحتاج إلى فحص يدوي. أرقام الدوال المتداخلة تظهر أيضاً، ولا يثبت الاستيراد تنفيذ المسار وقت التشغيل.
