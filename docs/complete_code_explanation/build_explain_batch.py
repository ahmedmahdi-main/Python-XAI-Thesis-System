import hashlib,json,pathlib
base=pathlib.Path(__file__).resolve().parent; root=base.parents[1]
groups={
'src/xai_finance/explain/shap_explain.py':[
(1,2,'يستورد NumPy للمصفوفات وSHAP للمفسرات وكائن Explanation؛ مكتبتان خارجيتان.'),
(5,6,'explain_shap تقبل اسم النموذج وكائنه وbackground وطلباً يحوي observations وnames، وتعيد Explanation. يستدعيها مسار توليد التفسيرات؛ تفترض توافق الأشكال والأسماء.'),
(7,10,'للخطي يفك الخطوات الثلاث scaler وselector وregressor من Pipeline، ويحول الخلفية والمشاهدات باستخدام المعاملات الملائمة ثم يستعمل LinearExplainer. تغيير ترتيب الخطوات يفشل هذا الافتراض.'),
(11,13,'ينشئ مصفوفة أصفار كشكل المشاهدات ويضع قيم السمات المختارة في retained_ ثم يعيد Explanation بمرجع التفسير وبيانات وأسماء المجال الأصلي؛ الأصفار للسمات التي حذفها selector لا تثبت عدم أهميتها في نموذج بديل.'),
(14,18,'للغابة والتعزيز ينشئ TreeExplainer مع خلفية وfeature_perturbation="interventional"، ويفسر المشاهدات مع check_additivity ثم يضيف الأسماء ويعيد التفسير. آلية الإخفاء والخلفية تؤثران في الإسناد.'),
(19,21,'لأي اسم آخر ينشئ Independent masker من الخلفية وPermutationExplainer يستدعي model.predict ببذرة وأسماء؛ عدد تقييمات الطلب cycles×(2p+1) حيث p عدد الأعمدة، ودفعات 256. هذا تقريب يعتمد ميزانية التقييم وليس قيماً سببية.'),
(24,28,'shap_reconstruction تجمع base_values ومساهمات الصف وتقارنها بتنبؤ النموذج ضمن rtol=1e-4 وatol=1e-3؛ تعيد أعظم ومتوسط فرق مطلق، وترفع AssertionError عند فشل allclose. الجمع لا يثبت أداء النموذج أو سلامة تفسير سببي.')],
'src/xai_finance/explain/lime_explain.py':[
(1,2,'يستورد NumPy لتلميحات الأنواع وLimeTabularExplainer من مكتبة LIME الخارجية.'),
(5,7,'explain_lime تستقبل بيانات تدريب ودالة predict وعينة وقاموس إعداد؛ تنشئ مفسر انحدار بأسماء السمات وتقطيع مستمر وبذرة واختيار أعلى الأوزان. تطلب تفسير العينة باستخدام عشر سمات وعدد perturbations من samples. يعاد استخدام بيانات التدريب كمرجع لتوليد الجوار لا كدليل سببي.'),
(8,11,'تستخرج التنبؤ المحلي من البديل وتنبؤ النموذج على العينة ذات محور دفعة، وتبني قاموس الفرق المطلق وR² الجوار الموزون والبذرة وعدد العينات والأوزان، ثم تعيد كائن التفسير والتدقيق. قد يكون تقريب الجوار ضعيفاً خصوصاً في أبعاد مترابطة.')],
'src/xai_finance/explain/quality.py':[
(1,2,'NumPy للحسابات وspearmanr من SciPy لارتباط الرتب؛ مكتبتان خارجيتان.'),
(5,8,'attribution_stability تستقبل متجهي إسهام وتقارن قيمهما المطلقة؛ تختار أصغر 10 وعدد السمات وتحسب نسبة تداخل فهارس أعلى الإسهامات. تساوي 1 يدل على تطابق المجموعتين وفق ترتيب argsort، لا على تطابق القيم.'),
(9,10,'تحسب ارتباط Spearman للرتب المطلقة عند تغير كلا المتجهين، وتعطي None للقيمة غير المتاحة أو غير المنتهية؛ تعيد أيضاً توصيف نطاق اختبار بذرتين للعينة نفسها. المتجه الفارغ قد يسبب قسمة على صفر، وتفترض الدالة تطابق أطوال الإدخال.'),
(13,17,'lime_weight_vector تنشئ متجه أصفار بطول count وتملؤه بأوزان feature من explanation.as_map()[1]، ثم تعيده. السمات غير الظاهرة تبقى صفراً؛ هذا لا يثبت انعدام أهميتها خارج البديل المحدود. تفترض وجود المفتاح 1 وفهارس ضمن المجال.')]
}
manifest={}
for path,entries in groups.items():
 raw=(root/path).read_bytes(); source=raw.decode('utf-8').splitlines(); name=path.replace('/','_')+'.md'; out=['# شرح `'+path+'`','','الاقتباسات من المصدر؛ التفسير مراجعة يدوية لا إجراء حسابات جديدة.','']
 for start,end,desc in entries: out += [f'## الأسطر {start}–{end}' if start!=end else f'## السطر {start}','','```python',*source[start-1:end],'```','',desc,'']
 (base/'line_by_line'/name).write_text('\n'.join(out),encoding='utf-8')
 manifest[path]={'document':'line_by_line/'+name,'ranges':[[a,b] for a,b,_ in entries],'sha256':hashlib.sha256(raw).hexdigest(),'review':'مراجعة يدوية؛ غير مستقلة','quote_verification':'تطابق آلي مع المصدر'}
(base/'explain_batch_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
