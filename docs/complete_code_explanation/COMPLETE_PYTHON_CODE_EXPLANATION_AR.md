# دليل الدراسة: حالة العمل

هذا الدليل **غير مكتمل**. الجرد الآلي والصفحات التمهيدية ودفعات الشرح السطري المنجزة متاحة أدناه. لا تعدّ القائمة الآلية بديلاً عن شرح كل ملف، ولم تُنجز بعد مراجعة النتائج من جميع ملفاتها ولا التدقيق الشامل للسطور والرسوم. لم تُعد نماذج التدريب أو تُغيّر البيانات والنتائج.

- [جرد المصدر الآلي](12_CODE_INDEX_AR.md) و[البيانات القابلة للمعالجة](inventory.json).
- [لمحة عن النظام](01_SYSTEM_OVERVIEW_AR.md).
- [البيانات والنوافذ](03_DATA_PIPELINE_AR.md).
- [نماذج التنبؤ وLSTM](04_MACHINE_LEARNING_MODELS_AR.md).
- [SHAP وLIME](06_SHAP_LIME_EXPLANATION_AR.md).
- [المقاييس والنتائج](07_EVALUATION_AND_RESULTS_AR.md).
- [شرح التقسيم سطراً بسطر](line_by_line/src_xai_finance_data_split.py.md).
- [شرح Persistence سطراً بسطر](line_by_line/src_xai_finance_models_baselines.py.md).
- [تقرير التغطية والفجوات](COVERAGE_AR.md).

للمصادر الحالية انظر أيضاً [تدقيق النتائج](../RESULTS_AUDIT.md) و[النتائج المعاد حسابها](../RECONSTRUCTED_RESULTS.md) و[الافتراضات والانحرافات](../ASSUMPTIONS_AND_DEVIATIONS.md). هذه الوثائق الموجودة مسبقاً ليست جزءاً من إنجاز الشرح المطلوب بالكامل.

## دفعة الاستمرار: نقطة الدخول والواجهة

- [شرح main.py سطراً بسطر](line_by_line/main.py.md).
- [شرح dashboard/app.py سطراً بسطر](line_by_line/dashboard_app.py.md).
- [تبويبات Streamlit الثمانية](08_STREAMLIT_DASHBOARD_AR.md).
- [سجل الاستمرار](CONTINUATION_AR.md).

تتحقق أداة `audit_coverage.py` من بصمة المصدر والاقتباسات لهذه الدفعة؛ تظل المراجعة الأكاديمية والتغطية الكاملة غير مكتملتين.

## دفعة الاستمرار: السمات والنوافذ

- [features.py: المؤشرات والسمات](line_by_line/src_xai_finance_data_features.py.md).
- [windows.py: النوافذ ومحاذاة الهدف](line_by_line/src_xai_finance_data_windows.py.md).
- [preprocess.py: المقاييس التدريبية](line_by_line/src_xai_finance_data_preprocess.py.md).
- [مثال AAPL الفعلي](03_DATA_PIPELINE_AR.md#مثال-aapl-من-ملفات-محفوظة-لا-مثال-افتراضي).

- [data/validate.py: التحقق من الأسعار](line_by_line/src_xai_finance_data_validate.py.md).
- [io/data_sources.py: تنزيل اللقطات والتحقق منها](line_by_line/src_xai_finance_io_data_sources.py.md).

## دفعة النماذج والتدريب

- [مراجعة دفعة البيانات](DATA_REVIEW_AR.md).
- [الاستقلال العددي قبل OLS](line_by_line/src_xai_finance_models_linear_preprocess.py.md).
- [نماذج sklearn واختيارها](line_by_line/src_xai_finance_models_sklearn_models.py.md).
- [شرح LSTM سطراً بسطر](line_by_line/src_xai_finance_models_lstm_model.py.md) و[فصل LSTM الموسع](05_LSTM_DEEP_EXPLANATION_AR.md).
- [خط التدريب والتقييم وحفظ النتائج](line_by_line/src_xai_finance_pipelines_train.py.md).

## دفعة ملفات التفسير

- [شرح SHAP السطري](line_by_line/src_xai_finance_explain_shap_explain.py.md).
- [شرح LIME السطري](line_by_line/src_xai_finance_explain_lime_explain.py.md).
- [شرح اختبارات جودة التفسير](line_by_line/src_xai_finance_explain_quality.py.md).
- [مثال تفسير AAPL المحفوظ وحدوده](06_SHAP_LIME_EXPLANATION_AR.md).
- [خط توليد SHAP وLIME وحفظ آثارهما](line_by_line/src_xai_finance_pipelines_explain.py.md).

## التقييم والتحقق العلمي

- [المقاييس](line_by_line/src_xai_finance_evaluate_metrics.py.md) و[حالات السوق](line_by_line/src_xai_finance_evaluate_regimes.py.md).
- [تدقيق التجربة الأصلية](line_by_line/src_xai_finance_validation_audit.py.md) و[تصميم الأهداف والتقسيم](line_by_line/src_xai_finance_validation_design.py.md).
- [التشخيصات](line_by_line/src_xai_finance_validation_diagnostics.py.md) و[التجارب](line_by_line/src_xai_finance_validation_experiments.py.md) و[الإحصاء وbootstrap](line_by_line/src_xai_finance_validation_statistics.py.md).
- [رسوم التحقق](line_by_line/src_xai_finance_validation_figures.py.md) و[تقرير التحقق](line_by_line/src_xai_finance_validation_report.py.md).
- [الشرح الرياضي وحدود التحقق](07_EVALUATION_AND_RESULTS_AR.md) و[تحقيق خطأ LIME](06_SHAP_LIME_EXPLANATION_AR.md).

## تقارير التخزين والإعداد

- [خط التقرير](line_by_line/src_xai_finance_pipelines_report.py.md) و[التخزين والبصمات](line_by_line/src_xai_finance_storage.py.md) و[الإعدادات](line_by_line/src_xai_finance_config.py.md).

## نقاط الدخول والبيئة والحزم

- [واجهة الأوامر CLI](line_by_line/src_xai_finance_cli.py.md)، [البذور واختيار الجهاز](line_by_line/src_xai_finance_seed.py.md)، [تشخيص البيئة](line_by_line/src_xai_finance_environment.py.md).
- [التشغيل السريع](line_by_line/scripts_run_quick.py.md) و[التشغيل الكامل](line_by_line/scripts_run_full.py.md).
- [الحزمة الرئيسية](line_by_line/src_xai_finance___init__.py.md) و[حزمة التحقق](line_by_line/src_xai_finance_validation___init__.py.md).
- ملفات تهيئة الحزم الفارغة: [data](line_by_line/src_xai_finance_data___init__.py.md)، [evaluate](line_by_line/src_xai_finance_evaluate___init__.py.md)، [explain](line_by_line/src_xai_finance_explain___init__.py.md)، [io](line_by_line/src_xai_finance_io___init__.py.md)، [models](line_by_line/src_xai_finance_models___init__.py.md)، [pipelines](line_by_line/src_xai_finance_pipelines___init__.py.md)، [reports](line_by_line/src_xai_finance_reports___init__.py.md).

## الرسوم وتنسيق التحقق

- [رسوم التقارير وSHAP](line_by_line/src_xai_finance_reports_plots.py.md).
- [تهيئة بروتوكول التحقق](line_by_line/scripts_start_scientific_validation.py.md)، [تشغيل مراحله](line_by_line/scripts_run_scientific_validation.py.md)، [بناء تقريره](line_by_line/scripts_build_validation_report.py.md)، [تنزيل البيانات](line_by_line/scripts_download_data.py.md).

## الاختبارات

- [fixtures](line_by_line/tests_conftest.py.md)، [الواجهة](line_by_line/tests_test_dashboard.py.md)، [اتساق SHAP وLIME](line_by_line/tests_test_explain_consistency.py.md)، [تدريب LSTM الاختباري](line_by_line/tests_test_lstm_training.py.md).
- [المقاييس والنماذج](line_by_line/tests_test_metrics_and_models.py.md)، [تكامل لقطة المزود](line_by_line/tests_test_provider_integration.py.md)، [التحقق العلمي](line_by_line/tests_test_scientific_validation.py.md)، [سلامة الزمن](line_by_line/tests_test_temporal_integrity.py.md).

## أدوات التشغيل دون اتصال

- [الإطلاق](line_by_line/scripts_launch_demo.py.md)، [العرض دون اتصال](line_by_line/scripts_offline_demo.py.md)، [الإعداد دون اتصال](line_by_line/scripts_setup_offline.py.md)، [البحث عن Python CPU](line_by_line/scripts_bootstrap_cpu.py.md).
- [حارس الشبكة الاختباري](line_by_line/scripts_offline_guard_sitecustomize.py.md)، [فحص البيئة](line_by_line/scripts_verify_environment.py.md)، [فحص حفظ الأدلة](line_by_line/scripts_verify_preservation_cpu.py.md).
- [SETUP_DEMO.bat](line_by_line/SETUP_DEMO.bat.md) و[START_DEMO.bat](line_by_line/START_DEMO.bat.md): اقتباسات وتدقيق بصمة مستقلان عن مقام Python.

## معالج النشر

- [شرح demo_wizard.py](line_by_line/scripts_demo_wizard.py.md): سلامة الحزمة، تثبيت CPU، تشغيل الخادم وإيقاف العملية المسجلة.

## فحوص الإعادة والحساسية

- [دقة إعادة تركيب السعر](line_by_line/scripts_audit_reconstruction_precision.py.md)، [تشخيص إعادة التشغيل بين الأجهزة](line_by_line/scripts_diagnose_validation_replay.py.md)، [فحص العرض دون اتصال](line_by_line/scripts_offline_smoke.py.md)، [إعادة تدريب LSTM للتحقق](line_by_line/scripts_replicate_validation_lstm.py.md).

## حزم العرض والتحقق

- [الحزمة البحثية السابقة](line_by_line/scripts_generate_defense_package.py.md)، [حزمة CPU](line_by_line/scripts_package_cpu_defense.py.md)، [ملحق التحقق العلمي](line_by_line/scripts_package_scientific_validation.py.md).

## فحوص نشر الواجهة

- [فحص Streamlit](line_by_line/scripts_check_dashboard_cpu.py.md)، [فحص Edge](line_by_line/scripts_browser_smoke_cpu.py.md)، [اختبار الإعداد والإطلاق](line_by_line/scripts_test_deployment_cpu.py.md).

## تدقيق الآثار وإعادة التشغيل

- [تدقيق آثار التجربة الأصلية](line_by_line/scripts_verify_artifacts.py.md)، [إعادة تشغيل CPU](line_by_line/scripts_verify_cpu_replay.py.md)، [تدقيق التحقق العلمي](line_by_line/scripts_verify_scientific_validation.py.md).

## سكربتات نشر خارج جرد 77

- [الفحص الأولي للأدلة](line_by_line/artifacts_deployment_initial_check.py.md)، [قبول الإصدار النهائي](line_by_line/artifacts_deployment_verify_final_release.py.md). دُققتا منفصلتين، وتستبعدان نسخ المصدر المحفوظة وأدوات إنشاء التوثيق من نطاق التطبيق.

## المراجعة العلمية الجارية

- [سجل المراجعة والتصحيحات وحدودها](SCIENTIFIC_REVIEW_AR.md).

- [المخططات العشرة للبنية والمسارات](02_PROJECT_ARCHITECTURE_AR.md) — حُللت وصُدرت آلياً؛ فُحص رسمان بصرياً فقط.
- [أسئلة الدفاع](11_DEFENSE_QUESTIONS_AND_ANSWERS_AR.md) — 100 سؤال، بانتظار مراجعة علمية وتحريرية شاملة.
- [الاختبارات والنشر](09_TESTS_AND_DEPLOYMENT_AR.md) و[حدود الاستنتاج](10_SCIENTIFIC_LIMITATIONS_AR.md).


## نسخة HTML للمراجعة

- [مسودة الكتاب العربي الموحد](ARABIC_TECHNICAL_BOOK_DRAFT.html): تضم الفصول و100 سؤال وصفحات الشرح السطري. فُحصت بنيتها آلياً فقط؛ لم يثبت عرض العربية أو ترقيم الصفحات أو صلاحية الطباعة، وتظهر Mermaid كشيفرة.

- [سجل التسليم المؤقت وحالات التحقق](DELIVERY_MANIFEST_AR.md).

## نسخة مراجعة مرئية بالرسوم

- [HTML موحد بصور SVG مدمجة](ARABIC_TECHNICAL_BOOK_FIGURES.html) و[PDF للمراجعة](ARABIC_TECHNICAL_BOOK_FIGURES_REVIEW_V5.pdf). يعرضان الأشكال ولا يثبتان اكتمال المراجعة الأكاديمية؛ راجع سجل التسليم للفحوص وحدودها.

- [جرد الرسوم وصفحاتها في PDF](DIAGRAM_INVENTORY_AR.md).

## تقارير تدقيق الجودة الجارية

- [مصفوفة مراجعة أسئلة الدفاع المئة](QUESTION_AUDIT_MATRIX_AR.md): حالات تتبع لا تثبت إكمال المراجعة العلمية الفردية.
- [تدقيق صفحات نسخة PDF للمراجعة](PAGE_QUALITY_AUDIT_AR.md): نتائج آلية وملاحظات بصرية وحدودها.
- [سجل المراجعة العلمية](SCIENTIFIC_REVIEW_AR.md) و[سجل التسليم](DELIVERY_MANIFEST_AR.md).

- [تدقيق صفحات نسخة البطاقات V2](PAGE_QUALITY_CARD_REVIEW_V2_AR.md): فحص آلي لكل صفحة ومعاينة مرئية جزئية فقط.
