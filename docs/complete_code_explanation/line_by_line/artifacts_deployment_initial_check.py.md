# شرح `artifacts/deployment/initial_check.py`

بصمة المصدر SHA-256: `8b17f8938e1f14907271816a38016de97415cf858c3cb36ab5f31f3778d989bc`.

سكربت نشر خارج جرد التطبيق الأصلي؛ لم يُنفذ هنا.

## الأسطر 1–5

```python
﻿import hashlib,json
from pathlib import Path
root=Path.cwd()
files=[p for folder in ['artifacts/runs','artifacts/scientific_validation','data/raw','data/manifests'] for p in (root/folder).rglob('*') if p.is_file()]
manifest={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
```

يستورد hashlib وjson وPath، ويعتبر مجلد العمل الجذر ويجمع ملفات النتائج والبيانات ويحفظ بصماتها في قاموس؛ يفترض التشغيل من جذر المشروع ويقرأ كل ملف كاملاً إلى الذاكرة.

## الأسطر 6–9

```python
output=root/'artifacts/deployment/original_evidence_sha256.json'
if output.exists(): raise RuntimeError('Preservation baseline already exists')
output.write_text(json.dumps(manifest,indent=2))
print('Preservation baseline:',len(files),'files;',sum(p.stat().st_size for p in files)/1024**2,'MiB',flush=True)
```

يحدد ملف baseline ويرفض الكتابة إن وجد ثم يكتب البصمات ويطبع العدد والحجم؛ له أثر كتابة ولا يجوز تشغيله لاستبدال الأدلة.

## الأسطر 10–15

```python
from streamlit.testing.v1 import AppTest
app=AppTest.from_file(str(root/'main.py'),default_timeout=90).run()
print('Exceptions:',[e.message for e in app.exception])
print('Title:',[x.value for x in app.title]);print('Tabs:',[x.label for x in app.tabs]);print('Datasets:',app.selectbox(key='asset').options)
assert not app.exception
assert len(app.tabs)==8
```

يشغل Streamlit AppTest على main.py ويطبع الاستثناءات والعنوان والتبويبات والأصول ويفرض عدم وجود استثناء وثمانية تبويبات؛ قد يفشل قبل assertions إذا لم يوجد عنصر الاختيار. لم ينفذ هنا.
