import hashlib,json,pathlib,re
base=pathlib.Path(__file__).resolve().parent; root=base.parents[1]
groups={
'SETUP_DEMO.bat':[(1,4,'يخفي عرض الأوامر ويعزل متغيرات البيئة ويغير القرص والمجلد إلى موقع batch ويحدد عنوان النافذة.'),(5,8,'إذا وجد Python داخل .demo_venv يشغل wizard setup مع جميع الوسائط %* ثم ينتقل إلى finished.'),(9,12,'وإلا إن وجد Python في .venv يشغل الإعداد به وينتقل إلى النهاية؛ مجرد وجود الملف لا يضمن سلامة البيئة.'),(13,20,'يبحث عن py دون إظهار الخرج، ثم يتحقق من Python 3.12 ويشغل wizard عبره إن توفر. فحص الإصدار هنا لا يتحقق صراحة من معمارية 64 بت.'),(21,27,'إن وجد python في PATH يستدعي bootstrap_cpu للبحث عن إصدار مناسب؛ وإلا يعرض تعليمات وينهي برمز 1.'),(28,32,'label finished يحفظ errorlevel ويعرض رسالة عند الفشل، ويتوقف للقراءة ما لم يُضبط XAI_DEMO_NO_PAUSE=1، ثم يعيد رمز النتيجة.')],
'START_DEMO.bat':[(1,4,'يعزل البيئة ويحدد مجلد batch وعنوان نافذة العرض ويخفي الأوامر.'),(5,9,'يتحقق من وجود مفسر .demo_venv، ويعرض تعليمات الإعداد ويتوقف اختيارياً ويخرج برمز 1 إن غاب.'),(10,14,'إن كان الوسيط الأول stop ينتقل إلى الفرع المعني؛ وإلا ينفذ wizard start مع جميع الوسائط ثم ينتقل إلى finished. فرع stop يستدعي wizard stop دون تمرير بقية الوسائط.'),(15,18,'يحفظ رمز الخروج ويتوقف اختيارياً عند الفشل فقط ثم يعيده للبيئة المستدعية.')]
}
manifest={}
for path,entries in groups.items():
 raw=(root/path).read_bytes(); lines=raw.decode('utf8').splitlines(); digest=hashlib.sha256(raw).hexdigest(); name=path+'.md'; out=['# شرح `'+path+'`','',f'بصمة المصدر SHA-256: `{digest}`.','','لا ينفذ هذا الشرح ملفات التشغيل.','']
 for a,b,d in entries: out += [f'## الأسطر {a}–{b}','','```bat',*lines[a-1:b],'```','',d,'']
 (base/'line_by_line'/name).write_text('\n'.join(out),encoding='utf8'); manifest[path]={'document':'line_by_line/'+name,'ranges':[[a,b] for a,b,_ in entries],'sha256':digest}
(base/'batch_files_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
for path,e in manifest.items():
 raw=(root/path).read_bytes(); assert hashlib.sha256(raw).hexdigest()==e['sha256']; lines=raw.decode('utf8').splitlines(); doc=(base/e['document']).read_text(encoding='utf8'); blocks=re.findall(r'```bat\n(.*?)\n```',doc,re.S); assert len(blocks)==len(e['ranges'])
 for (a,b),block in zip(e['ranges'],blocks): assert block=='\n'.join(lines[a-1:b]),(path,a,b)
print('verified batch files',len(manifest),'blocks',sum(len(e['ranges']) for e in manifest.values()))
