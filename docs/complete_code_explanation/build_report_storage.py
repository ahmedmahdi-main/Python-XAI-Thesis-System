import hashlib,json,pathlib
base=pathlib.Path(__file__).resolve().parent; root=base.parents[1]
groups={
'src/xai_finance/storage.py':[
(1,5,'hashlib وjson وPath قياسية وNumPy خارجية لتحويل الأنواع العددية.'),
(8,10,'sha256 تفتح ملفاً ثنائياً وتحسب بصمته عبر file_digest وتعيد السلسلة الست عشرية؛ تتحقق من سلامة البايتات مقارنة بمرجع موثوق لا هوية المصدر وحدها.'),
(13,20,'json_default تحول عدد NumPy إلى قيمة Python ومصفوفته إلى قائمة وPath إلى نص؛ ترفع TypeError للنوع غير المدعوم. تستعمل عند تسلسل JSON.'),
(23,25,'write_json تنشئ مجلد الأب وتكتب JSON بتنسيق indent=2 وUTF-8 مع محول الأنواع ورفض NaN؛ الكتابة تستبدل الملف إن وجد وليست ذرية صراحة.'),
(28,29,'read_json تقرأ UTF-8 وتفك JSON وتعيد محتواه، وتسمح لأخطاء غياب الملف أو فساد البيانات بالانتشار.')],
'src/xai_finance/config.py':[
(1,3,'Path قياسية وyaml خارجية لقراءة الإعدادات.'),
(5,10,'project_root تبحث أولاً في مجلد العمل ثم أسلاف ملف الوحدة عن configs/datasets.yaml وpyproject.toml؛ تعيد أول مطابقة أو ترفع RuntimeError. قد يحدد مجلد عمل مطابق مشروعاً قبل موقع الوحدة.'),
(13,13,'ROOT يحسب عند استيراد الوحدة، لذا قد يفشل الاستيراد خارج شجرة مشروع مناسبة.'),
(16,21,'load_config تقرأ YAML المدخل بترميز UTF-8 وsafe_load ثم تضيف datasets من إعداد المشروع وتعيد القاموس؛ لا تتحقق هنا من صحة المخطط وتستبدل المفتاح datasets إن كان موجوداً.')],
'src/xai_finance/pipelines/report.py':[
(1,14,'استيرادات قياسية للوقت والمسار والنسخ، وخارجية للرسوم والمصفوفات والجداول وPlotly، وداخلية للمقاييس والنماذج والرسوم والتخزين.'),
(17,30,'generate_report تقرأ run.json وتولد رسم التدفق وتقارير الأصول، وتكتب summary والنتائج وتغير status وتسجل بصمات القفل والشفرة ثم تكتب الفهرس. تشغيلها يغير ملفات التجربة ولم يجر هنا.'),
(33,49,'asset_report تقرأ التدقيق والمقاييس والتنبؤات وتتحقق من المقاييس وتولد رسوم التنبؤ والخطأ والخسارة والإضافات والمعاملات وHTML مستقل Plotly، وتعيد ملخص الأصل مع توفر التفسيرات. قد تفشل إذا غاب أثر مطلوب.'),
(52,58,'verify_saved_metrics تعيد حساب المقاييس الخمسة من التنبؤات حسب النموذج وتقارن القيم غير None بالمحفوظة بتسامح 1e-8؛ هذه مقارنة عددية وليست فحصاً شاملاً للمصدر أو لكل الحقول.'),
(61,73,'extra_charts ترسم MAE بحسب الحالة من regimes.json، ثم تقرأ النوافذ وترسم أهداف التقسيم مع الوحدات وتحفظ الرسوم.'),
(74,84,'لكل نموذج ترسم مصفوفة الالتباس الثنائية المحفوظة بخلايا وأسماء not up وup ومحاور التنبؤ والواقع ثم تحفظ الشكل؛ التعادل يندرج في not up.'),
(87,96,'export_coefficients يحمل النماذج ويفك Pipeline، ويعيد معاملات OLS إلى وحدات مدخلات أصلية بتقسيمها على scale ويضع صفراً للأعمدة المستبعدة؛ الثابت الجديد intercept−Σ(coef_original×mean). يكتب المعاملات والثابت وتدقيق الرتبة، والصفر الناتج من اختيار الأساس لا يثبت انعدام أهمية اقتصادية.'),
(99,100,'research_limitations تعيد قائمة نصوص تقيد الاستنساخ والبيانات المعدلة والإسكان وR² والتفسير والعشوائية والتقسيم؛ لا تجري اختباراً.'),
(103,114,'write_research_markdown تكتب لكل أصل جدولا للمقاييس بوحداته وتواريخه وقيوده ثم تحفظ RESULTS.md وتنسخها إلى docs/RECONSTRUCTED_RESULTS.md؛ النسخ قد يستبدل المستند السابق عند تشغيل الدالة.'),
(117,119,'write_inventory تحسب بصمات جميع ملفات المجلد باستثناء inventory.json وverification.json وتكتب JSON؛ هذا جرد سلامة نسبي لا يتضمن الملفين المستبعدين.')]
}
manifest={}
for path,entries in groups.items():
 raw=(root/path).read_bytes(); src=raw.decode('utf8').splitlines(); digest=hashlib.sha256(raw).hexdigest(); name=path.replace('/','_')+'.md'; out=['# شرح `'+path+'`','',f'بصمة المصدر SHA-256: `{digest}`.','','الاقتباسات من المصدر؛ لم تنفذ أعمال التقرير أو تعدل البيانات.','']
 for start,end,desc in entries: out += [f'## الأسطر {start}–{end}','','```python',*src[start-1:end],'```','',desc,'']
 (base/'line_by_line'/name).write_text('\n'.join(out),encoding='utf8')
 manifest[path]={'document':'line_by_line/'+name,'ranges':[[a,b] for a,b,_ in entries],'sha256':digest,'review':'مراجعة يدوية غير مستقلة','quote_verification':'آلي'}
(base/'report_storage_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
