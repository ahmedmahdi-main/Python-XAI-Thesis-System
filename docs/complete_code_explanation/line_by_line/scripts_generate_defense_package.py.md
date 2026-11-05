# شرح `scripts/generate_defense_package.py`

بصمة المصدر SHA-256: `4f8457037544d7d5e285652c9a8844a8b0921d836db77e8ea901252821b95b5e`.

لم تنفذ عمليات النسخ أو الحزم في جلسة التوثيق.

## الأسطر 1–8

```python
from pathlib import Path
import shutil
import zipfile

from xai_finance.config import ROOT
from xai_finance.pipelines.train import resolve_run
from xai_finance.config import load_config
from xai_finance.storage import sha256, write_json
```

Path وshutil وzipfile قياسية؛ ROOT وتحميل الإعداد والتشغيل والبصمات والتخزين داخلية.

## الأسطر 11–21

```python
def copy_project(destination: Path, run_folder: Path) -> None:
    for name in ["src", "dashboard", "configs", "docs", "scripts", "tests", ".streamlit", "wheelhouse"]:
        shutil.copytree(ROOT / name, destination / name, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    for name in ["pyproject.toml", "requirements-lock.txt", "requirements-gpu.txt", "README.md", "CODEX_XAI_THESIS_IMPLEMENTATION_PLAN.md"]:
        shutil.copy2(ROOT / name, destination / name)
    for name in ["raw", "manifests"]:
        shutil.copytree(ROOT / "data" / name, destination / "data" / name, dirs_exist_ok=True)
    shutil.copytree(run_folder, destination / "artifacts/runs" / run_folder.name, dirs_exist_ok=True)
    for name in ["tests", "environment"]:
        shutil.copytree(ROOT / "artifacts" / name, destination / "artifacts" / name, dirs_exist_ok=True)
    shutil.copy2(ROOT / "artifacts/latest_full.json", destination / "artifacts/latest_full.json")
```

copy_project تنسخ الشيفرة والإعدادات والوثائق والعجلات واللقطات والتشغيل وآثار الاختبارات والبيئة والمؤشر إلى الوجهة؛ dirs_exist_ok يسمح بالدمج مع ملفات موجودة وقد يستبدل نسخاً، فلا يعني إنشاء حزمة معزولة تلقائياً.

## الأسطر 24–31

```python
def archive_package(destination: Path, run_id: str) -> Path:
    backup_folder = ROOT / "backups"
    backup_folder.mkdir(exist_ok=True)
    archive = backup_folder / f"defense_{run_id}.zip"
    with zipfile.ZipFile(archive, "w", allowZip64=True) as bundle:
        for path in sorted(destination.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(destination), compress_type=zipfile.ZIP_STORED)
```

archive_package تنشئ backups وتفتح ZIP باسم التشغيل بوضع w وتضيف الملفات دون ضغط؛ وضع w يمكنه استبدال ملف موجود بالاسم نفسه، ولذلك هذا السكربت أقدم من ضمان عدم الاستبدال في حزمة CPU.

## الأسطر 32–36

```python
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("Defense ZIP CRC verification failed")
    write_json(archive.with_suffix(".sha256.json"), {"archive": archive.name, "sha256": sha256(archive), "backup_scope": "Local same-disk backup; second physical medium/cloud copy not verified"})
    return archive
```

تفحص CRC باستخدام testzip وتكتب JSON لبصمة ZIP ثم تعيد المسار؛ النسخة على القرص نفسه ولا تثبت نسخة خارجية.

## الأسطر 39–50

```python
def main() -> None:
    destination = (ROOT / "defense_package").resolve()
    if not destination.is_relative_to(ROOT.resolve()):
        raise ValueError("Defense package must stay inside project workspace")
    destination.mkdir(exist_ok=True)
    run_folder = resolve_run(load_config(ROOT / "configs/full_experiment.yaml"))
    copy_project(destination, run_folder)
    entries = {str(path.relative_to(destination)).replace("\\", "/"): sha256(path) for path in sorted(destination.rglob("*")) if path.is_file() and path.name != "PACKAGE_MANIFEST.json"}
    write_json(destination / "PACKAGE_MANIFEST.json", {"run_id": run_folder.name, "files": entries, "platform": "Windows CPython 3.12 AMD64 wheels; Python installer not bundled"})
    archive = archive_package(destination, run_folder.name)
    print("Defense package:", destination)
    print("CRC-checked backup:", archive)
```

main تحدد مجلد defense_package داخل الجذر وتتحقق من احتوائه وتنسخ تجربة full وتحسب بصمات الملفات عدا manifest ثم تكتب فهرساً وتحزم وتطبع؛ لها آثار نسخ وكتابة.

## الأسطر 53–54

```python
if __name__ == "__main__":
    main()
```

حارس التنفيذ المباشر يستدعي main؛ لم يشغل هنا.
