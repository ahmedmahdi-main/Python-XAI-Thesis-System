"""Package the executed addendum separately from the untouched defense bundle."""
import argparse
import base64
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image

from xai_finance.config import ROOT
from xai_finance.storage import sha256, write_json


class EmbeddedImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attributes):
        if tag == "img":
            self.sources.append(dict(attributes)["src"])


def verify_offline_page(destination: Path) -> None:
    parser = EmbeddedImages()
    parser.feed((destination / "offline_validation.html").read_text(encoding="utf-8"))
    figures = sorted((destination / "figures").glob("*.png"))
    assert len(parser.sources) == len(figures) == 5
    for source, path in zip(parser.sources, figures):
        assert source.startswith("data:image/png;base64,")
        assert base64.b64decode(source.split(",", 1)[1]) == path.read_bytes()
        with Image.open(path) as chart:
            chart.verify()
    write_json(destination / "offline_page_verification.json", {"embedded_pngs": len(figures), "all_image_bytes_match_exports": True, "png_decoding_verified": True, "requires_network": False})


def snapshot_source(destination: Path) -> None:
    snapshot = destination / "source_snapshot"
    snapshot.mkdir(exist_ok=False)
    paths = [path for category in ["src", "scripts", "tests", "configs"] for path in (ROOT / category).rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.suffix in {".py", ".yaml"}]
    paths.extend(ROOT / name for name in ["pyproject.toml", "requirements-lock.txt", "requirements-gpu.txt", "docs/SCIENTIFIC_VALIDATION_REPRODUCIBILITY.md", "docs/SCIENTIFIC_VALIDATION_REPORT.md"])
    for path in paths:
        target = snapshot / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def package_addendum(destination: Path) -> None:
    paths = sorted(path for path in destination.rglob("*") if path.is_file())
    manifest = {str(path.relative_to(destination)): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in paths}
    write_json(destination / "addendum_manifest.json", manifest)
    archive = ROOT / "backups" / f"{destination.name}_addendum.zip"
    with ZipFile(archive, "x", compression=ZIP_DEFLATED, compresslevel=6) as bundle:
        for path in paths + [destination / "addendum_manifest.json"]:
            bundle.write(path, path.relative_to(destination).as_posix())
    with ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert len(bundle.infolist()) == len(paths) + 1
        for relative, record in manifest.items():
            archived = bundle.read(relative.replace("\\", "/"))
            assert len(archived) == record["bytes"]
            assert hashlib.sha256(archived).hexdigest() == record["sha256"]
    write_json(destination / "addendum_archive.json", {"path": str(archive.relative_to(ROOT)), "bytes": archive.stat().st_size, "sha256": sha256(archive), "manifest_files": len(manifest), "archive_crc_verified": True, "archive_member_sha256_verified": True})
    print(f"Separate addendum: {archive}; SHA256 {sha256(archive)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    destination = parser.parse_args().folder.resolve()
    verify_offline_page(destination)
    snapshot_source(destination)
    package_addendum(destination)


if __name__ == "__main__":
    main()
