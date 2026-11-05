# شرح `artifacts/deployment/verify_final_release.py`

بصمة المصدر SHA-256: `69b3222f1d90e10e8cb48a987a7c6e227dccc72ad9efa8084f7d623f9f2a51cc`.

سكربت نشر خارج جرد التطبيق الأصلي؛ لم يُنفذ هنا.

## الأسطر 1–8

```python
"""Final distribution acceptance, independent of the archive builder."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

```

سلسلة توثيق واستيرادات قياسية لـ CLI والبصمات وJSON والمسارات وZIP.

## الأسطر 9–17

```python
root = Path(__file__).resolve().parents[2]
archive = root / "Mohammad_XAI_Defense_CPU.zip"
candidate = root / "dist/CPU_Candidate.zip"
parser = argparse.ArgumentParser()
parser.add_argument("--destination", type=Path, default=root / "dist/final_release_acceptance")
args = parser.parse_args()
destination = args.destination.resolve()
assert destination.is_relative_to(root.resolve())
assert not destination.exists(), "Do not overwrite a previous extracted verification"
```

يحدد الجذر والأرشيف النهائي والمرشح ووجهة الاستخراج، ويتحقق من بقاء الوجهة في الجذر وعدم وجودها؛ يعتمد على assert الذي يمكن تعطيله في Python المحسن.

## الأسطر 18–25

```python
with archive.open("rb") as stream:
    archive_hash = hashlib.file_digest(stream, "sha256").hexdigest()
assert archive_hash == archive.with_suffix(".zip.sha256").read_text().split()[0]
prefix = "Mohammad_XAI_Defense_CPU/"
with zipfile.ZipFile(archive) as final, zipfile.ZipFile(candidate) as tested:
    assert final.testzip() is None
    manifest = json.loads(final.read(prefix + "CPU_PACKAGE_MANIFEST.json"))
    prior = json.loads(tested.read(prefix + "CPU_PACKAGE_MANIFEST.json"))
```

يحسب بصمة أرشيف الإصدار ويقارن ملف sha256، ثم يفتح الإصدار والمرشح ويفحص CRC ويقرأ manifest لكل منهما.

## الأسطر 26–35

```python
    changed = []
    for relative, old in prior["files"].items():
        assert relative in manifest["files"], f"Tested file omitted: {relative}"
        if manifest["files"][relative]["sha256"] != old["sha256"]:
            changed.append(relative)
    allowed = {"docs/CPU_DEPLOYMENT_REPORT.md", "scripts/package_cpu_defense.py"}
    assert all(p in allowed or p.startswith("artifacts/deployment/") for p in changed), changed
    assert all("/.demo_venv/" not in n and "/.venv/" not in n and "/provider_cache/" not in n for n in final.namelist())
    assert all((destination / name).resolve().is_relative_to(destination.resolve()) for name in final.namelist())
    final.extractall(destination)
```

يتحقق من احتواء ملفات المرشح ويجمع الملفات التي تغيرت، ويسمح بتغييرات محددة أو تحت artifacts/deployment، ويفحص استبعاد بعض البيئات ومسارات الاستخراج، ثم يستخرج الأرشيف. المسار والروابط داخل ZIP تحتاج سياق نظام الملفات، ولا يدعي الفحص صحة كل استخدام محتمل.

## الأسطر 36–41

```python
package = destination / "Mohammad_XAI_Defense_CPU"
for relative, expected in manifest["files"].items():
    path = package / relative
    assert path.stat().st_size == expected["bytes"], relative
    with path.open("rb") as stream:
        assert hashlib.file_digest(stream, "sha256").hexdigest() == expected["sha256"], relative
```

لكل ملف بالفهرس يفحص الحجم وبصمة SHA-256 بعد الاستخراج؛ يفترض سلامة الفهرس ووجهته ويتطلب قراءة الملفات.

## الأسطر 42–44

```python
receipt = {"status": "PASSED", "archive": str(archive), "bytes": archive.stat().st_size, "sha256": archive_hash, "manifest_files": len(manifest["files"]), "crc": "PASSED", "all_extracted_member_sizes_and_sha256": "PASSED", "tested_candidate_runtime_wheels_and_research_evidence": "BYTE_IDENTICAL", "changed_tested_members": changed, "fresh_extraction": str(package), "bundled_virtual_environments": False, "original_evidence_files": manifest["original_evidence_files_included_unchanged"], "dependency_wheels": manifest["dependency_wheels"]}
(root / "artifacts/deployment/final_release.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
print(json.dumps(receipt, indent=2), flush=True)
```

يبني إيصال نجاح ويكتبه في artifacts/deployment/final_release.json ويطبعه؛ التنفيذ يكتب ويستخرج ملفات ولم يحدث هنا.
