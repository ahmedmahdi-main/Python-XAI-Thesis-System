import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def json_default(content):
    if isinstance(content, (np.integer, np.floating)):
        return content.item()
    if isinstance(content, np.ndarray):
        return content.tolist()
    if isinstance(content, Path):
        return str(content)
    raise TypeError(f"Unsupported JSON type: {type(content)}")


def write_json(path: Path, content: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2, default=json_default, allow_nan=False), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
