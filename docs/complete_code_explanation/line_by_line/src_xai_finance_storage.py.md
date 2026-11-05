# شرح `src/xai_finance/storage.py`

بصمة المصدر SHA-256: `8975cad5dd0e2c315d38ccdfdb293750a7f2d2e1b294d52143b28da19a44e96d`.

الاقتباسات من المصدر؛ لم تنفذ أعمال التقرير أو تعدل البيانات.

## الأسطر 1–5

```python
import hashlib
import json
from pathlib import Path

import numpy as np
```

hashlib وjson وPath قياسية وNumPy خارجية لتحويل الأنواع العددية.

## الأسطر 8–10

```python
def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()
```

sha256 تفتح ملفاً ثنائياً وتحسب بصمته عبر file_digest وتعيد السلسلة الست عشرية؛ تتحقق من سلامة البايتات مقارنة بمرجع موثوق لا هوية المصدر وحدها.

## الأسطر 13–20

```python
def json_default(content):
    if isinstance(content, (np.integer, np.floating)):
        return content.item()
    if isinstance(content, np.ndarray):
        return content.tolist()
    if isinstance(content, Path):
        return str(content)
    raise TypeError(f"Unsupported JSON type: {type(content)}")
```

json_default تحول عدد NumPy إلى قيمة Python ومصفوفته إلى قائمة وPath إلى نص؛ ترفع TypeError للنوع غير المدعوم. تستعمل عند تسلسل JSON.

## الأسطر 23–25

```python
def write_json(path: Path, content: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2, default=json_default, allow_nan=False), encoding="utf-8")
```

write_json تنشئ مجلد الأب وتكتب JSON بتنسيق indent=2 وUTF-8 مع محول الأنواع ورفض NaN؛ الكتابة تستبدل الملف إن وجد وليست ذرية صراحة.

## الأسطر 28–29

```python
def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
```

read_json تقرأ UTF-8 وتفك JSON وتعيد محتواه، وتسمح لأخطاء غياب الملف أو فساد البيانات بالانتشار.
