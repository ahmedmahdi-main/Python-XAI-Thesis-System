import pathlib,hashlib,json
base=pathlib.Path(__file__).resolve().parent; root=base.parents[1]
groups={
'artifacts/deployment/initial_check.py':[(1,5,'يستورد hashlib وjson وPath، ويعتبر مجلد العمل الجذر ويجمع ملفات النتائج والبيانات ويحفظ بصماتها في قاموس؛ يفترض التشغيل من جذر المشروع ويقرأ كل ملف كاملاً إلى الذاكرة.'),(6,9,'يحدد ملف baseline ويرفض الكتابة إن وجد ثم يكتب البصمات ويطبع العدد والحجم؛ له أثر كتابة ولا يجوز تشغيله لاستبدال الأدلة.'),(10,15,'يشغل Streamlit AppTest على main.py ويطبع الاستثناءات والعنوان والتبويبات والأصول ويفرض عدم وجود استثناء وثمانية تبويبات؛ قد يفشل قبل assertions إذا لم يوجد عنصر الاختيار. لم ينفذ هنا.')],
'artifacts/deployment/verify_final_release.py':[(1,8,'سلسلة توثيق واستيرادات قياسية لـ CLI والبصمات وJSON والمسارات وZIP.'),(9,17,'يحدد الجذر والأرشيف النهائي والمرشح ووجهة الاستخراج، ويتحقق من بقاء الوجهة في الجذر وعدم وجودها؛ يعتمد على assert الذي يمكن تعطيله في Python المحسن.'),(18,25,'يحسب بصمة أرشيف الإصدار ويقارن ملف sha256، ثم يفتح الإصدار والمرشح ويفحص CRC ويقرأ manifest لكل منهما.'),(26,35,'يتحقق من احتواء ملفات المرشح ويجمع الملفات التي تغيرت، ويسمح بتغييرات محددة أو تحت artifacts/deployment، ويفحص استبعاد بعض البيئات ومسارات الاستخراج، ثم يستخرج الأرشيف. المسار والروابط داخل ZIP تحتاج سياق نظام الملفات، ولا يدعي الفحص صحة كل استخدام محتمل.'),(36,41,'لكل ملف بالفهرس يفحص الحجم وبصمة SHA-256 بعد الاستخراج؛ يفترض سلامة الفهرس ووجهته ويتطلب قراءة الملفات.'),(42,44,'يبني إيصال نجاح ويكتبه في artifacts/deployment/final_release.json ويطبعه؛ التنفيذ يكتب ويستخرج ملفات ولم يحدث هنا.')]
}
manifest={}
for path,entries in groups.items():
 raw=(root/path).read_bytes(); src=raw.decode('utf8').splitlines(); digest=hashlib.sha256(raw).hexdigest(); name=path.replace('/','_')+'.md'; out=['# شرح `'+path+'`','',f'بصمة المصدر SHA-256: `{digest}`.','','سكربت نشر خارج جرد التطبيق الأصلي؛ لم يُنفذ هنا.','']
 for a,b,d in entries: out += [f'## الأسطر {a}–{b}','','```python',*src[a-1:b],'```','',d,'']
 (base/'line_by_line'/name).write_text('\n'.join(out),encoding='utf8'); manifest[path]={'document':'line_by_line/'+name,'ranges':[[a,b] for a,b,_ in entries],'sha256':digest,'physical_lines':len(src)}
(base/'deployment_extra_sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
