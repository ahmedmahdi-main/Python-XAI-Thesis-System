# شرح `scripts/verify_preservation_cpu.py`

بصمة المصدر SHA-256: `e5e9a23eec4d3bd30edd2548337ed4386f87d04483d598c9bb8366ede1ed9a51`.

وصف ثابت؛ لم تُشغّل السكربتات.

## الأسطر 1–8

```python
"""Confirm every original research evidence file matches the pre-repair baseline."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
```

التوثيق يصف مقارنة الأدلة بمرجع؛ argparse وhashlib وjson وPath قياسية، وROOT أصل المشروع.

## الأسطر 11–13

```python
def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()
```

digest تقرأ ملفاً ثنائياً وتحسب SHA-256؛ تعيد بصمة النص الست عشري.

## الأسطر 16–23

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/deployment/preservation.json")
    args = parser.parse_args()
    baseline = ROOT / "artifacts/deployment/original_evidence_sha256.json"
    entries = json.loads(baseline.read_text(encoding="utf-8"))
    mismatches = [relative for relative, expected in entries.items() if not (ROOT / relative).is_file() or digest(ROOT / relative) != expected]
    assert not mismatches, mismatches
```

main تقرأ خيار output الافتراضي وملف baseline ذي البصمات، وتجمع الملفات الناقصة أو المختلفة وتفرض عدم وجود مخالفات. يعتمد الاستنتاج على شمول وموثوقية baseline؛ assert يمكن تعطيله بوضع Python المحسن.

## الأسطر 24–27

```python
    receipt = {"status": "PASSED", "original_evidence_files": len(entries), "mismatches": mismatches, "baseline_sha256": digest(baseline), "protected_run": "full_20261021T040901084647Z", "protected_validation": "validation_20261021T055002439194Z"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"PRESERVATION PASS: {len(entries)} original evidence files unchanged")
```

تكتب إيصال نجاح يتضمن عدد الأدلة وبصمة baseline وأسماء التشغيلات المحمية، وتنشئ مجلد الوجهة وتطبع النجاح؛ هذا الفحص يكتب ملفاً افتراضياً داخل artifacts إذا شُغّل ولم يشغل هنا.

## الأسطر 30–31

```python
if __name__ == "__main__":
    main()
```

حارس التنفيذ يستدعي main.
