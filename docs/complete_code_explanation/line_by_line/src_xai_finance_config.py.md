# شرح `src/xai_finance/config.py`

بصمة المصدر SHA-256: `cd4bc1670b874ac8c6d41fb3552d077f5d6d6289e3e217c117c5a8d7742944df`.

الاقتباسات من المصدر؛ لم تنفذ أعمال التقرير أو تعدل البيانات.

## الأسطر 1–3

```python
from pathlib import Path

import yaml
```

Path قياسية وyaml خارجية لقراءة الإعدادات.

## الأسطر 5–10

```python
def project_root() -> Path:
    candidates = [Path.cwd(), *Path(__file__).resolve().parents]
    for candidate in candidates:
        if (candidate / "configs/datasets.yaml").exists() and (candidate / "pyproject.toml").exists():
            return candidate
    raise RuntimeError("Run from the research/defense project directory containing configs/datasets.yaml")
```

project_root تبحث أولاً في مجلد العمل ثم أسلاف ملف الوحدة عن configs/datasets.yaml وpyproject.toml؛ تعيد أول مطابقة أو ترفع RuntimeError. قد يحدد مجلد عمل مطابق مشروعاً قبل موقع الوحدة.

## الأسطر 13–13

```python
ROOT = project_root()
```

ROOT يحسب عند استيراد الوحدة، لذا قد يفشل الاستيراد خارج شجرة مشروع مناسبة.

## الأسطر 16–21

```python
def load_config(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as stream:
        configuration = yaml.safe_load(stream)
    with (ROOT / "configs/datasets.yaml").open(encoding="utf-8") as stream:
        configuration["datasets"] = yaml.safe_load(stream)["datasets"]
    return configuration
```

load_config تقرأ YAML المدخل بترميز UTF-8 وsafe_load ثم تضيف datasets من إعداد المشروع وتعيد القاموس؛ لا تتحقق هنا من صحة المخطط وتستبدل المفتاح datasets إن كان موجوداً.
