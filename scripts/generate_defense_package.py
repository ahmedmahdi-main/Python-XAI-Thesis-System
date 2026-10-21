from pathlib import Path
import shutil
import zipfile

from xai_finance.config import ROOT
from xai_finance.pipelines.train import resolve_run
from xai_finance.config import load_config
from xai_finance.storage import sha256, write_json


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


def archive_package(destination: Path, run_id: str) -> Path:
    backup_folder = ROOT / "backups"
    backup_folder.mkdir(exist_ok=True)
    archive = backup_folder / f"defense_{run_id}.zip"
    with zipfile.ZipFile(archive, "w", allowZip64=True) as bundle:
        for path in sorted(destination.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(destination), compress_type=zipfile.ZIP_STORED)
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("Defense ZIP CRC verification failed")
    write_json(archive.with_suffix(".sha256.json"), {"archive": archive.name, "sha256": sha256(archive), "backup_scope": "Local same-disk backup; second physical medium/cloud copy not verified"})
    return archive


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


if __name__ == "__main__":
    main()
