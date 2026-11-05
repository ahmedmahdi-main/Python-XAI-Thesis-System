# شرح `scripts/run_scientific_validation.py`

بصمة المصدر SHA-256: `9d8bd2280e9ea79bc236f77c96d0db1ef051b5c6959e8fa8ada72518f76e3741`.

الاقتباسات من الملف؛ لم تُشغّل السكربتات أو تجاربها.

## الأسطر 1–8

```python
"""Run additive validation without touching the original run or defense bundle."""
import argparse
from pathlib import Path

from xai_finance.config import ROOT
from xai_finance.storage import read_json
from xai_finance.validation.audit import audit_original
from xai_finance.validation.experiments import aggregate_experiments, run_experiments
```

التوثيق يصف تحققاً إضافياً؛ argparse وPath قياسيتان، والبقية وظائف داخلية للقراءة والتدقيق وتشغيل وتجميع التجارب.

## الأسطر 11–18

```python
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("action", choices=["audit", "train", "aggregate"])
    arguments = parser.parse_args()
    destination = arguments.folder.resolve()
    protocol = read_json(destination / "protocol.json")
    original = ROOT / "artifacts/runs" / protocol["original_run"]
```

main تحلل مجلد الوجهة والعمل audit أو train أو aggregate، ثم تقرأ البروتوكول وتحدد التشغيل الأصلي المشار إليه.

## الأسطر 19–25

```python
    if arguments.action == "audit":
        audit_original(original, destination)
    elif arguments.action == "train":
        run_experiments({"protocol": protocol, "destination": destination, "original": original})
        aggregate_experiments(destination)
    else:
        aggregate_experiments(destination)
```

audit يستدعي فحص الأصل؛ train يشغل التجارب ثم يجمعها؛ aggregate يجمع فقط. هذه الأوامر تحسب أو تدرب وتكتب في الوجهة؛ لم تشغل أثناء التوثيق.

## الأسطر 28–29

```python
if __name__ == "__main__":
    main()
```

حارس التنفيذ المباشر يستدعي main.
