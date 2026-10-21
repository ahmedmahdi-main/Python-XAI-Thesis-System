"""Run additive validation without touching the original run or defense bundle."""
import argparse
from pathlib import Path

from xai_finance.config import ROOT
from xai_finance.storage import read_json
from xai_finance.validation.audit import audit_original
from xai_finance.validation.experiments import aggregate_experiments, run_experiments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("action", choices=["audit", "train", "aggregate"])
    arguments = parser.parse_args()
    destination = arguments.folder.resolve()
    protocol = read_json(destination / "protocol.json")
    original = ROOT / "artifacts/runs" / protocol["original_run"]
    if arguments.action == "audit":
        audit_original(original, destination)
    elif arguments.action == "train":
        run_experiments({"protocol": protocol, "destination": destination, "original": original})
        aggregate_experiments(destination)
    else:
        aggregate_experiments(destination)


if __name__ == "__main__":
    main()
