"""Confirm every original research evidence file matches the pre-repair baseline."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/deployment/preservation.json")
    args = parser.parse_args()
    baseline = ROOT / "artifacts/deployment/original_evidence_sha256.json"
    entries = json.loads(baseline.read_text(encoding="utf-8"))
    mismatches = [relative for relative, expected in entries.items() if not (ROOT / relative).is_file() or digest(ROOT / relative) != expected]
    assert not mismatches, mismatches
    receipt = {"status": "PASSED", "original_evidence_files": len(entries), "mismatches": mismatches, "baseline_sha256": digest(baseline), "protected_run": "full_20261021T040901084647Z", "protected_validation": "validation_20261021T055002439194Z"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"PRESERVATION PASS: {len(entries)} original evidence files unchanged")


if __name__ == "__main__":
    main()
