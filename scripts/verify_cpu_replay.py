"""Read-only CPU replay and fresh explanation probes; never rewrite research evidence."""

import argparse
import importlib
import json
import os
from pathlib import Path
import pkgutil
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".demo_runtime/matplotlib"))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/deployment/cpu_replay.json")
    args = parser.parse_args()
    original_connect = socket.socket.connect

    def connect(connection, address):
        if isinstance(address, tuple) and address[0] not in {"127.0.0.1", "localhost", "::1"}:
            raise RuntimeError(f"External connection denied: {address}")
        return original_connect(connection, address)

    socket.socket.connect = connect
    import numpy as np
    import torch
    import xai_finance
    from threadpoolctl import threadpool_limits
    from verify_artifacts import verify_asset
    from verify_scientific_validation import replay_job, verify_aggregate
    from xai_finance.explain.lime_explain import explain_lime
    from xai_finance.explain.shap_explain import explain_shap, shap_reconstruction
    from xai_finance.pipelines.train import load_models, load_windows
    from xai_finance.seed import seed_experiment
    from xai_finance.storage import read_json, sha256

    assert torch.__version__ == "2.5.1+cpu", torch.__version__
    assert torch.version.cuda is None
    assert not torch.cuda.is_available()
    seed_experiment(42)
    torch.set_num_threads(4)
    imports = []
    for module in pkgutil.walk_packages(xai_finance.__path__, "xai_finance."):
        importlib.import_module(module.name)
        imports.append(module.name)
    run = ROOT / "artifacts/runs/full_20261021T040901084647Z"
    for relative, digest in read_json(run / "inventory.json").items():
        assert sha256(run / relative) == digest, relative
    assets = []
    probes = []
    with threadpool_limits(limits=4):
        for asset in read_json(run / "run.json")["assets_completed"]:
            assets.append(verify_asset(run / asset))
            print(f"CPU REPLAY PASS: {asset}: four models, metrics, SHAP/LIME", flush=True)
        windows = load_windows(run / "AAPL")
        models = load_models(run / "AAPL", "cpu")
        assert models["LSTM"].device.type == "cpu"
        training = windows.flat[windows.partitions["train"]]
        background = training[np.linspace(0, len(training)-1, 4, dtype=int)]
        observation = windows.flat[windows.partitions["test"][:1]]
        for name, model in models.items():
            before = model.predict(observation).copy()
            explanation = explain_shap(name, model, background, {"observations": observation, "names": windows.flat_names, "seed": 42, "cycles": 1})
            shap_audit = shap_reconstruction(explanation, before)
            _, lime_audit = explain_lime(training, model.predict, observation[0], {"names": windows.flat_names, "seed": 42, "samples": 100})
            np.testing.assert_array_equal(before, model.predict(observation))
            assert np.isfinite(lime_audit["weighted_neighborhood_r2"])
            probes.append({"asset": "AAPL", "model": name, "shap": shap_audit, "lime": lime_audit, "scope": "fresh bounded compatibility probe on existing model; not replacement research evidence"})
            print(f"FRESH CPU SHAP/LIME PASS: {name}", flush=True)
        validation = ROOT / "artifacts/scientific_validation/validation_20261021T055002439194Z"
        jobs = sorted((validation / "experiments").rglob("completion.json"))
        assert len(jobs) == 15
        replay = []
        for job in jobs:
            replay.append(replay_job(job.parent, run))
            print(f"VALIDATION CPU REPLAY PASS: {job.parent.relative_to(validation)}", flush=True)
        aggregate = verify_aggregate(validation)
    receipt = {"status": "PASSED", "torch": torch.__version__, "cuda_available": False, "external_python_connections": "denied", "modules_imported": imports, "assets": assets, "fresh_explanation_probes": probes, "scientific_validation_jobs": replay, "scientific_validation_aggregate": aggregate}
    destination = args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(receipt, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
