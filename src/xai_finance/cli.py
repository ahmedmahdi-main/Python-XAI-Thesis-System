import argparse
import os

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

from xai_finance.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproducible thesis reconstruction")
    parser.add_argument("command", choices=["doctor", "download", "validate", "train", "explain", "evaluate", "report", "all"])
    parser.add_argument("--config", default="configs/default.yaml")
    arguments = parser.parse_args()
    configuration = load_config(arguments.config)
    execute(arguments.command, configuration)


def execute(command: str, configuration: dict) -> None:
    from xai_finance.io.data_sources import download_all, load_snapshot
    from xai_finance.pipelines.train import resolve_run, train_experiment

    if command == "doctor":
        from xai_finance.environment import verify_environment
        verify_environment()
    if command in {"download", "all"}:
        download_all(configuration)
    if command == "validate":
        for asset in configuration["assets"]:
            prices, manifest = load_snapshot(asset)
            print(asset, len(prices), manifest["sha256"])
    if command in {"train", "all"}:
        train_experiment(configuration)
    if command in {"explain", "all"}:
        from xai_finance.pipelines.explain import explain_experiment
        explain_experiment(resolve_run(configuration))
    if command in {"evaluate", "report", "all"}:
        from xai_finance.pipelines.report import generate_report
        generate_report(resolve_run(configuration))


if __name__ == "__main__":
    main()
