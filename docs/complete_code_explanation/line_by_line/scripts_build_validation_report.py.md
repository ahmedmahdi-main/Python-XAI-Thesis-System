# شرح `scripts/build_validation_report.py`

بصمة المصدر SHA-256: `6359790f490bf1d13a23bfe3df70dff0c33b589ab3a1f483255f8d4249e98d32`.

الاقتباسات من الملف؛ لم تُشغّل السكربتات أو تجاربها.

## الأسطر 1–7

```python
import argparse
import base64
import html
from pathlib import Path

from xai_finance.storage import read_json
from xai_finance.validation.report import write_report
```

argparse وbase64 وhtml وPath قياسية، وread_json وwrite_report من المشروع.

## الأسطر 10–18

```python
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    destination = parser.parse_args().folder.resolve()
    write_report(destination)
    figures = []
    for path in sorted((destination / "figures").glob("*.png")):
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        figures.append(f'<figure><figcaption>{html.escape(path.stem.replace("_", " "))}</figcaption><img alt="{html.escape(path.stem)}" src="data:image/png;base64,{encoded}"></figure>')
```

main تقرأ مجلد التحقق وتستدعي كتابة التقرير، ثم تجمع صور PNG وترمز بايتاتها base64 في figure وتقوم بتهريب العناوين. يستلزم write_report آثاراً سابقة ويولد تقارير ورسومات.

## الأسطر 19–24

```python
    report = html.escape((destination / "SCIENTIFIC_VALIDATION_REPORT.md").read_text(encoding="utf-8"))
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><title>XAI scientific validation</title><style>body{max-width:1200px;margin:40px auto;padding:20px;font:16px system-ui;background:#f7f8fa;color:#17212b}img{max-width:100%}pre{white-space:pre-wrap;font:14px monospace;overflow-wrap:anywhere}figure{background:white;padding:20px;margin:30px 0}figcaption{font-size:22px}</style><h1>Scientific validation: evidence and limitations</h1><p>Offline supplement; original defense package preserved unchanged.</p>' + ''.join(figures) + '<h2>Full report</h2><pre>' + report + '</pre></html>'
    (destination / "offline_validation.html").write_text(page, encoding="utf-8")
    assert read_json(destination / "verification.json")["preservation"]["mismatches"] == []
    print(destination / "SCIENTIFIC_VALIDATION_REPORT.md")
    print(destination / "offline_validation.html")
```

تهرب نص Markdown وتدرجه كما هو داخل pre في صفحة HTML إنجليزية ذات صور مدمجة offline، وتكتب الصفحة ثم تؤكد خلو mismatches في verification.json وتطبع المسارات. فحص المحافظة يأتي بعد الكتابة وليس قبلها؛ الصفحة لا تحقق متطلبات التقرير العربي RTL.

## الأسطر 27–28

```python
if __name__ == "__main__":
    main()
```

حارس التنفيذ يستدعي main.
