# تقرير التغطية المؤقت

النطاق: main.py ومجلدات dashboard وsrc وscripts وtests. تستبعد البيئات ونسخ المصدر المولّدة تحت artifacts؛ يلزم البت في سكربتات artifacts/deployment المستقلة. ملفات batch والإعدادات ليست في المقام.

- الجرد: 77 ملفاً، 3929 سطراً فعلياً؛ الأسطر التنفيذية التقريبية: 3181.
- مقياس بدايات رموز Python غير التعليقات: 3210 من 3210 (100.00%). لا يحسب كل أسطر السلاسل متعددة الأسطر، ولا يقيس جودة الشرح الأكاديمي.
- صفحات يدوية تغطي جميع بدايات الرموز في الجرد: 77؛ ملفات فيها فجوات: 0.
- يتحقق هذا التدقيق من بصمات المصدر واقتباسات جميع دفعات manifest المشمولة آلياً؛ تدقق stamp_source_versions.py بصمات صفحات الشرح مقابل الجرد وتدرجها في الصفحات. تدقق أداة verify_legacy_quotes.py اقتباسات الصفحتين الأقدم وبصمتيهما؛ شغّلها مع هذا التدقيق.
- المراجعة الأكاديمية: تفسيرات الصفحات روجعت يدوياً مقابل المصدر؛ لم يختبر تشغيل الواجهة، ولم تُراجع الشروح مراجعة مستقلة. لا يدل التطابق النصي على صحة التفسير.

## الملفات المغطاة بمقياس بدايات الرموز

- `main.py`
- `dashboard/app.py`
- `scripts/audit_reconstruction_precision.py`
- `scripts/bootstrap_cpu.py`
- `scripts/browser_smoke_cpu.py`
- `scripts/build_validation_report.py`
- `scripts/check_dashboard_cpu.py`
- `scripts/demo_wizard.py`
- `scripts/diagnose_validation_replay.py`
- `scripts/download_data.py`
- `scripts/generate_defense_package.py`
- `scripts/launch_demo.py`
- `scripts/offline_demo.py`
- `scripts/offline_guard/sitecustomize.py`
- `scripts/offline_smoke.py`
- `scripts/package_cpu_defense.py`
- `scripts/package_scientific_validation.py`
- `scripts/replicate_validation_lstm.py`
- `scripts/run_full.py`
- `scripts/run_quick.py`
- `scripts/run_scientific_validation.py`
- `scripts/setup_offline.py`
- `scripts/start_scientific_validation.py`
- `scripts/test_deployment_cpu.py`
- `scripts/verify_artifacts.py`
- `scripts/verify_cpu_replay.py`
- `scripts/verify_environment.py`
- `scripts/verify_preservation_cpu.py`
- `scripts/verify_scientific_validation.py`
- `src/xai_finance/__init__.py`
- `src/xai_finance/cli.py`
- `src/xai_finance/config.py`
- `src/xai_finance/data/__init__.py`
- `src/xai_finance/data/features.py`
- `src/xai_finance/data/preprocess.py`
- `src/xai_finance/data/split.py`
- `src/xai_finance/data/validate.py`
- `src/xai_finance/data/windows.py`
- `src/xai_finance/environment.py`
- `src/xai_finance/evaluate/__init__.py`
- `src/xai_finance/evaluate/metrics.py`
- `src/xai_finance/evaluate/regimes.py`
- `src/xai_finance/explain/__init__.py`
- `src/xai_finance/explain/lime_explain.py`
- `src/xai_finance/explain/quality.py`
- `src/xai_finance/explain/shap_explain.py`
- `src/xai_finance/io/__init__.py`
- `src/xai_finance/io/data_sources.py`
- `src/xai_finance/models/__init__.py`
- `src/xai_finance/models/baselines.py`
- `src/xai_finance/models/linear_preprocess.py`
- `src/xai_finance/models/lstm_model.py`
- `src/xai_finance/models/sklearn_models.py`
- `src/xai_finance/pipelines/__init__.py`
- `src/xai_finance/pipelines/explain.py`
- `src/xai_finance/pipelines/report.py`
- `src/xai_finance/pipelines/train.py`
- `src/xai_finance/reports/__init__.py`
- `src/xai_finance/reports/plots.py`
- `src/xai_finance/seed.py`
- `src/xai_finance/storage.py`
- `src/xai_finance/validation/__init__.py`
- `src/xai_finance/validation/audit.py`
- `src/xai_finance/validation/design.py`
- `src/xai_finance/validation/diagnostics.py`
- `src/xai_finance/validation/experiments.py`
- `src/xai_finance/validation/figures.py`
- `src/xai_finance/validation/report.py`
- `src/xai_finance/validation/statistics.py`
- `tests/conftest.py`
- `tests/test_dashboard.py`
- `tests/test_explain_consistency.py`
- `tests/test_lstm_training.py`
- `tests/test_metrics_and_models.py`
- `tests/test_provider_integration.py`
- `tests/test_scientific_validation.py`
- `tests/test_temporal_integrity.py`

## الفجوات: أرقام أسطر بدايات الرموز غير المشروحة

النطاقات تجمع الأسطر المتتالية فقط؛ التعليقات والأسطر الفارغة وأسطر استمرار السلاسل لا تدخل هذا المقياس.


المطلوب أيضاً: تدقيق الاقتباسات والتفسير لجميع الصفحات، وفصل تغطية الأكواد عن الجودة، وإكمال الفصول والرسوم والأمثلة الفعلية والاختبارات والنشر وأسئلة الدفاع والتقرير القابل للطباعة. لا يجوز ادعاء اكتمال 100%.


## نطاق موسع مستقل

وُجد سكربتان من شيفرة المشروع تحت artifacts/deployment خارج جرد 77: initial_check.py وverify_final_release.py. تدقق verify_deployment_extra.py بصمتيهما واقتباساتهما و57 بداية رمز فيهما؛ معهما يصبح النطاق الموسع 79 ملفاً و3267 بداية رمز عند نجاح جميع التدقيقات. لا يشمل ذلك نسخ المصدر المحفوظة أو سكربتات توليد وتدقيق هذا التوثيق. هذه الأرقام لا تثبت اكتمال الشرح الأكاديمي أو دقة النتائج.
