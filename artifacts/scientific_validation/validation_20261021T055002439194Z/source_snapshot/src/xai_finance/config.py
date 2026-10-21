from pathlib import Path

import yaml

def project_root() -> Path:
    candidates = [Path.cwd(), *Path(__file__).resolve().parents]
    for candidate in candidates:
        if (candidate / "configs/datasets.yaml").exists() and (candidate / "pyproject.toml").exists():
            return candidate
    raise RuntimeError("Run from the research/defense project directory containing configs/datasets.yaml")


ROOT = project_root()


def load_config(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as stream:
        configuration = yaml.safe_load(stream)
    with (ROOT / "configs/datasets.yaml").open(encoding="utf-8") as stream:
        configuration["datasets"] = yaml.safe_load(stream)["datasets"]
    return configuration
