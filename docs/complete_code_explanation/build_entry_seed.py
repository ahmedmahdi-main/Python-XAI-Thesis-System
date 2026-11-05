import hashlib,json,pathlib
base=pathlib.Path(__file__).resolve().parent; root=base.parents[1]
groups={
'src/xai_finance/cli.py':[(1,6,'argparse وos من المكتبة القياسية. setdefault يضبط إعداد CUBLAS إن لم يكن موجوداً قبل استيراد بقية المسار؛ لا يستبدل قيمة موجودة. load_config داخلي لقراءة YAML.'),(9,15,'main ينشئ محلل سطر الأوامر ويحدد command من الخيارات وconfig الافتراضي، ويقرأ الوسائط والإعداد ثم يستدعي execute؛ الوسيط غير الصالح يوقف argparse برسالة.'),(18,20,'execute تستقبل الأمر والقاموس وتستورد تحميل البيانات والتدريب وحل مسار التشغيل؛ الاستيراد مؤجل إلى الاستدعاء.'),(22,30,'doctor يستدعي فحص البيئة؛ download وall يستدعيان تنزيل أو تحقق اللقطات؛ validate يحمل كل أصل ويفحصه ويطبع العدد والبصمة. هذه فروع مستقلة وليست سلسلة elif.'),(31,38,'train وall يدربان؛ explain وall يفسران آخر تشغيل؛ evaluate وreport وall تستدعي جميعاً generate_report، الذي يقرأ المقاييس ويعيد التحقق ويكتب تقارير. all يسير وفق ترتيب الفروع؛ تشغيل هذه الأوامر قد ينشئ آثاراً ولم ينفذ للتوثيق.'),(41,42,'حارس __main__ يشغّل main عند التنفيذ كوحدة أو ملف، وليس عند الاستيراد المعتاد.')],
'src/xai_finance/seed.py':[(1,7,'os وrandom قياسيتان؛ يضبط setdefault إعداد CUBLAS قبل تحميل NumPy وtorch الخارجيتين ولا يغير قيمة سابقة.'),(10,19,'seed_experiment يثبت بذور random وNumPy وTorch وCUDA، ويفرض خوارزميات حتمية، ويعطل benchmark وTF32 ويحدد أربعة خيوط. يغير الحالة العامة للعملية وقد يرفع خطأ لخوارزمية غير حتمية؛ لا يضمن تطابقاً بين كل الإصدارات والأجهزة.'),(22,30,'select_device تقبل cpu أو auto أو cuda. تعيد CPU فور طلبه، وترفض قيمة غير معروفة، وتختبر تخصيص CUDA وحساباً صغيراً إن كان متاحاً قبل إرجاع الجهاز والسبب.'),(31,37,'عند فشل CUDA تعيد CPU في auto أو تعيد رفع الاستثناء للطلب الصريح؛ وعند غيابه ترفض cuda وتختار CPU لـ auto. الاختبار لا يضمن ذاكرة كافية للتدريب كاملاً.')],
'src/xai_finance/environment.py':[(1,8,'json قياسية وtorch خارجية؛ ROOT وsoftware_environment والبذرة واختيار الجهاز وwrite_json من المشروع.'),(11,19,'verify_environment تثبت بذرة 42 وتختار الجهاز، وتبني LSTM تشخيصية بثماني سمات و16 مخفية على مدخل عشوائي 8×30×8 وتجري backward على متوسط مربع الخرج، وتتحقق من finiteness للخرج ثم تجمع معلومات البيئة. هذا اختبار عتاد عشوائي لا نتيجة مالية ولا يتحقق صراحة من finiteness كل تدرج.'),(20,24,'تضيف اسم GPU وذاكرته عند CUDA وتكتب التقرير في artifacts/environment/current.json وتطبعه؛ لها أثر كتابة وتغير البذور ولم تشغل هنا.')],
'scripts/run_quick.py':[(1,4,'os وPath وsubprocess وsys مكتبات قياسية للمسارات وبيئة وتشغيل عملية Python.'),(6,9,'يستخرج الجذر من موقع السكربت ويعين PYTHONHASHSEED وCUBLAS لعملية الابن ثم يشغل CLI all بتهيئة quick_demo وفي الجذر؛ check=True يرفع خطأ عند فشل الأمر. هذه نقطة دخول ذات آثار تنزيل وتدريب وتفسير وتقارير ولم تشغل هنا.')],
'scripts/run_full.py':[(1,4,'os وPath وsubprocess وsys قياسية لاختيار الجذر وتشغيل عملية فرعية.'),(6,9,'يعين جذر المشروع وبذرة الهاش وإعداد CUBLAS ويشغل CLI all مع full_experiment.yaml؛ check=True يكشف فشل العملية. تنفيذ السكربت يجري سير التجربة الكامل ولم يحدث هنا.')],
'src/xai_finance/__init__.py':[(1,1,'سلسلة توثيق تصف الحزمة بأنها تنبؤ زمني وتفسيرات لاحقة؛ لا تنفذ تدريباً.'),(3,3,'يعين __version__ إلى 0.1.0 كبيان إصدار الحزمة؛ لا يثبت إصدار البيئة أو البيانات.')],
'src/xai_finance/validation/__init__.py':[(1,1,'سلسلة توثيق تصف التحقق الإضافي واستعمال الآثار المجمدة مدخلات للقراءة؛ لا تنفذ فحصاً بنفسها.')]
}
for folder in ('data','evaluate','explain','io','models','pipelines','reports'):
 groups[f'src/xai_finance/{folder}/__init__.py']=[]
manifest={}
for path,entries in groups.items():
 raw=(root/path).read_bytes(); source=raw.decode('utf8').splitlines(); digest=hashlib.sha256(raw).hexdigest(); name=path.replace('/','_')+'.md'
 out=['# شرح `'+path+'`','',f'بصمة المصدر SHA-256: `{digest}`.','','تفسير مقابل المصدر، لم تُشغّل الأوامر الموثقة.','']
 if not entries: out+=['الملف فارغ عند البصمة المذكورة؛ لا يحتوي أسطراً أو استيرادات أو دوال، ويحدد مجلد الحزمة عند الاستيراد.','']
 for start,end,desc in entries: out += [f'## الأسطر {start}–{end}','','```python',*source[start-1:end],'```','',desc,'']
 (base/'line_by_line'/name).write_text('\n'.join(out),encoding='utf8')
 manifest[path]={'document':'line_by_line/'+name,'ranges':[[a,b] for a,b,_ in entries],'sha256':digest,'review':'مراجعة يدوية غير مستقلة','quote_verification':'آلي'}
(base/'entry_seed_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
