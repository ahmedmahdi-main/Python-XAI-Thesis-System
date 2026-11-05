# شرح `scripts/package_cpu_defense.py`

بصمة المصدر SHA-256: `631f1680abb55b54d04c551386248d9e7dc89e93c90eac85a6d8f55394b2025b`.

لم تنفذ عمليات النسخ أو الحزم في جلسة التوثيق.

## الأسطر 1–16

```python
"""Build an exclusive, hash-verified CPU package without replacing older archives."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()
```

توثيق واستيرادات قياسية، وROOT، وdigest لحساب SHA-256 لملف ثنائي.

## الأسطر 19–28

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, default=ROOT / "Mohammad_XAI_Defense_CPU.zip")
    args = parser.parse_args()
    archive = args.archive.resolve()
    if not archive.is_relative_to(ROOT.resolve()) or archive.suffix != ".zip":
        raise ValueError("The archive must be a ZIP inside this workspace.")
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        raise FileExistsError(f"Refusing to overwrite an existing defense archive: {archive}")
```

main تقبل archive وتفرض امتداد ZIP ووجوده داخل الجذر، وتنشئ الأب وترفض أرشيفاً موجوداً؛ لا تنفذ الحزم أثناء التوثيق.

## الأسطر 29–37

```python
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = ROOT / "dist" / f"cpu_build_{timestamp}" / "Mohammad_XAI_Defense_CPU"
    destination.mkdir(parents=True, exist_ok=False)
    receipt = json.loads((ROOT / "artifacts/deployment/windows_deployment.json").read_text())
    assert receipt["status"] == "PASSED"
    wheels = sorted((ROOT / "wheelhouse-cpu").glob("*.whl"))
    assert len(wheels) == 90, f"Expected 89 pinned dependencies plus project wheel, found {len(wheels)}"
    assert any(p.name.startswith("torch-2.5.1+cpu-") for p in wheels)
    assert not any("nvidia" in p.name or "+cu121" in p.name for p in wheels)
```

تحدد مجلد بناء زمني جديداً، وتقرأ إيصال النشر وتؤكد نجاحه ووجود 90 عجلة وtorch CPU وعدم وجود عجلات CUDA/NVIDIA؛ assertions قد تُعطل في Python المحسن.

## الأسطر 38–50

```python
    for name in ["src", "dashboard", "configs", "docs", "scripts", "tests", ".streamlit", "wheelhouse-cpu"]:
        print(f"Copying {name}", flush=True)
        shutil.copytree(ROOT / name, destination / name, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    for name in ["main.py", "SETUP_DEMO.bat", "START_DEMO.bat", "README.md", "pyproject.toml", "requirements-cpu.txt", "requirements-gpu.txt", "requirements-lock.txt", "CODEX_XAI_THESIS_IMPLEMENTATION_PLAN.md", ".env.example"]:
        shutil.copy2(ROOT / name, destination / name)
    for name in ["raw", "manifests"]:
        shutil.copytree(ROOT / "data" / name, destination / "data" / name)
    # Include every research run, including retained superseded diagnostic runs.
    for name in ["runs", "scientific_validation", "environment", "tests"]:
        print(f"Copying all artifacts/{name}", flush=True)
        shutil.copytree(ROOT / "artifacts" / name, destination / "artifacts" / name)
    for pointer in (ROOT / "artifacts").glob("latest*.json"):
        shutil.copy2(pointer, destination / "artifacts" / pointer.name)
```

تنسخ المصدر والوثائق والإعدادات والعجلات واللقطات وجميع تشغيلات البحث والتحقق وآثار البيئة والاختبارات ومؤشرات latest، مع استبعاد ذاكرات Python من المصدر.

## الأسطر 51–63

```python
    evidence = destination / "artifacts/deployment"
    evidence.mkdir(parents=True)
    external_release_receipts = {"package.json", "final_release.json", "final_release_check.log", "release_build.log"}
    for path in (ROOT / "artifacts/deployment").iterdir():
        if path.is_file() and path.suffix in {".json", ".xml", ".log"} and path.name not in external_release_receipts:
            shutil.copy2(path, evidence / path.name)
    for folder in (ROOT / "artifacts/deployment").glob("browser*"):
        if folder.is_dir() and (folder / "receipt.json").exists():
            target = evidence / folder.name
            target.mkdir()
            for path in folder.iterdir():
                if path.suffix == ".png" or path.name == "receipt.json":
                    shutil.copy2(path, target / path.name)
```

تنسخ إيصالات نشر مختارة عدا إيصالات الإصدار الخارجي، وصور وإيصالات متصفح فقط من المجلدات المطابقة.

## الأسطر 64–71

```python
    baseline = json.loads((evidence / "original_evidence_sha256.json").read_text())
    print(f"Verifying preservation of all {len(baseline)} original evidence files", flush=True)
    for relative, expected in baseline.items():
        assert (destination / relative).is_file(), f"Research evidence omitted: {relative}"
        assert digest(destination / relative) == expected, f"Research evidence changed: {relative}"
    entries = {p.relative_to(destination).as_posix(): {"bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(destination.rglob("*")) if p.is_file()}
    manifest = {"format": 1, "created_utc": datetime.now(timezone.utc).isoformat(), "platform": "Windows x64 CPython 3.12", "torch": "2.5.1+cpu", "dependency_wheels": len(wheels), "python_installer_bundled": False, "original_evidence_files_included_unchanged": len(baseline), "excluded_nonresearch_content": ["virtual environments", "pip caches", "provider cookies", "browser profiles", "Git metadata", "bytecode caches in active source", "older distribution archives (preserved in place)"], "files": entries}
    (destination / "CPU_PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
```

تقرأ بصمات الأدلة الأصلية وتتحقق من وجودها وتطابقها في staging، ثم تحصر الملفات وأحجامها وبصماتها وتكتب CPU_PACKAGE_MANIFEST. هذه سلامة مقابل baseline المسجل.

## الأسطر 72–80

```python
    pending = archive.with_suffix(".zip.pending")
    if pending.exists():
        raise FileExistsError(pending)
    print(f"Writing {len(entries)+1} files; all {len(baseline)} original evidence files included unchanged.", flush=True)
    with zipfile.ZipFile(pending, "x", allowZip64=True) as bundle:
        for path in sorted(destination.rglob("*")):
            if path.is_file():
                compression = zipfile.ZIP_STORED if path.suffix in {".whl", ".png", ".npz", ".docx", ".jpg"} else zipfile.ZIP_DEFLATED
                bundle.write(path, (Path(destination.name) / path.relative_to(destination)).as_posix(), compress_type=compression, compresslevel=6)
```

ترفض ملف pending موجوداً وتفتح ZIP حصرياً وتضيف الملفات باختيار ضغط بحسب الامتداد؛ لا تضغط عجلات وصوراً وأنواعاً مضغوطة مسبقاً.

## الأسطر 81–86

```python
    with zipfile.ZipFile(pending) as bundle:
        assert bundle.testzip() is None, "ZIP CRC failure"
        packaged = {name.removeprefix(destination.name + "/") for name in bundle.namelist()}
        assert packaged == set(entries) | {"CPU_PACKAGE_MANIFEST.json"}
        for relative, expected in entries.items():
            assert hashlib.sha256(bundle.read(destination.name + "/" + relative)).hexdigest() == expected["sha256"], relative
```

تفحص CRC وقائمة الأعضاء وبصمة كل عضو مقابل الفهرس؛ قد تستهلك الذاكرة عند قراءة عضو كبير كاملاً.

## الأسطر 87–93

```python
    # rename() refuses an existing destination on Windows, preserving prior packages.
    pending.rename(archive)
    archive_hash = digest(archive)
    archive.with_suffix(".zip.sha256").write_text(f"{archive_hash}  {archive.name}\n", encoding="ascii")
    verification = {"status": "PASSED", "archive": str(archive), "sha256": archive_hash, "bytes": archive.stat().st_size, "manifest_files": len(entries), "original_evidence_files": len(baseline), "dependency_wheels": len(wheels), "crc_and_all_member_sha256": "PASSED", "staging_folder": str(destination)}
    (ROOT / "artifacts/deployment/package.json").write_text(json.dumps(verification, indent=2), encoding="utf-8")
    print(json.dumps(verification, indent=2), flush=True)
```

تعيد تسمية pending إلى الأرشيف، وتحسب بصمته وتكتب ملف sha256 وإيصال package.json وتطبع التقرير؛ يلاحظ التعليق أن rename في Windows يرفض وجهة موجودة.

## الأسطر 96–97

```python
if __name__ == "__main__":
    main()
```

حارس التنفيذ يستدعي main.
