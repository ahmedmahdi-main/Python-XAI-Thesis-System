from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
import torch
from threadpoolctl import threadpool_limits

from xai_finance.explain.lime_explain import explain_lime
from xai_finance.explain.quality import attribution_stability, lime_weight_vector
from xai_finance.explain.shap_explain import explain_shap, shap_reconstruction
from xai_finance.pipelines.train import load_models, load_windows
from xai_finance.reports.plots import explanation_charts, save_figure
from xai_finance.seed import seed_experiment
from xai_finance.storage import read_json, write_json


def fixed_subset(indices: np.ndarray, count: int) -> np.ndarray:
    return indices[np.linspace(0, len(indices) - 1, min(count, len(indices)), dtype=int)]


def explain_experiment(folder: Path) -> None:
    metadata = read_json(folder / "run.json")
    configuration = metadata["configuration"]
    seed_experiment(configuration["seed"])
    for asset in configuration["assets"]:
        with threadpool_limits(limits=4):
            explain_asset(folder / asset, configuration)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    metadata["status"] = "TRAINED_AND_EXPLAINED"
    write_json(folder / "run.json", metadata)


def explain_asset(folder: Path, configuration: dict) -> None:
    windows = load_windows(folder)
    models = load_models(folder, configuration["device"])
    training = windows.flat[windows.partitions["train"]]
    background_indices = fixed_subset(windows.partitions["train"], configuration["background_samples"])
    background = windows.flat[background_indices]
    for name, model in models.items():
        count = configuration["lstm_explain_samples"] if name == "LSTM" else configuration["explain_samples"]
        indices = fixed_subset(windows.partitions["test"], count)
        request = {"observations": windows.flat[indices], "names": windows.flat_names, "seed": configuration["seed"], "cycles": configuration["permutation_cycles"]}
        context = {"folder": folder, "name": name, "model": model, "windows": windows, "indices": indices, "background_indices": background_indices, "background": background, "training": training, "configuration": configuration}
        print(f"{folder.name}: explaining {name}, {len(indices)} fixed test observations", flush=True)
        explain_model(context, request)


def explain_model(context: dict, request: dict) -> None:
    model, indices, windows = context["model"], context["indices"], context["windows"]
    folder = context["folder"] / context["name"] / "explanations"
    folder.mkdir(parents=True, exist_ok=True)
    started = perf_counter()
    before = model.predict(request["observations"])
    inference_seconds = perf_counter() - started
    started = perf_counter()
    explanation = explain_shap(context["name"], model, context["background"], request)
    shap_seconds = perf_counter() - started
    reconstruction = shap_reconstruction(explanation, before)
    np.savez_compressed(folder / "shap.npz", values=explanation.values, base_values=explanation.base_values, observations=request["observations"], indices=indices, feature_names=np.asarray(windows.flat_names))
    lime_audits, lime_explanations = explain_local_dates(context, folder)
    repeat_request = {**request, "seed": request["seed"] + 1, "observations": request["observations"][:1]}
    repeated = explain_shap(context["name"], model, context["background"], repeat_request)
    after = model.predict(request["observations"])
    np.testing.assert_array_equal(before, after)
    quality = {"shap_reconstruction": reconstruction, "prediction_unchanged_max_abs": float(np.max(np.abs(before - after))), "shap_elapsed_seconds": shap_seconds, "shap_samples": len(indices), "test_indices": indices.tolist(), "target_dates": [str(windows.targets[index].date()) for index in indices], "feature_cutoffs": [str(windows.origins[index].date()) for index in indices], "background_indices": context["background_indices"].tolist(), "background_max_target_date": str(windows.targets[context["background_indices"][-1]].date()), "shap_seed_stability": attribution_stability(explanation.values[0], repeated.values[0]), "lime_local": lime_audits, "lime_seed_stability": attribution_stability(lime_weight_vector(lime_explanations[0], len(windows.flat_names)), lime_weight_vector(lime_explanations[1], len(windows.flat_names))), "limitations": "Marginal masking and LIME neighborhoods can violate correlated technical-feature/time/OHLC constraints. Attributions are associations, not causality; global means cover only the declared subset."}
    quality["inference_elapsed_seconds_same_subset"] = inference_seconds
    quality["shap_overhead_ratio_same_subset"] = shap_seconds / max(inference_seconds, 1e-12)
    write_json(folder / "quality.json", quality)
    units = read_json(context["folder"] / "data_audit.json")["snapshot"]["units"]
    explanation_charts(explanation, folder, {"title": f"{context['folder'].name} | {context['name']} | {units}", "date": str(windows.targets[indices[0]].date()), "lookback": windows.x.shape[1], "features": windows.feature_names})
    save_regime_drivers(explanation.values, context, folder)


def explain_local_dates(context: dict, folder: Path) -> tuple[list[dict], list]:
    windows, configuration = context["windows"], context["configuration"]
    request = {"names": windows.flat_names, "seed": configuration["seed"], "samples": configuration["lime_samples"]}
    audits, first_explanation = [], None
    for index in context["indices"]:
        started = perf_counter()
        explanation, audit = explain_lime(context["training"], context["model"].predict, windows.flat[index], request)
        audit.update({"elapsed_seconds": perf_counter() - started, "target_date": str(windows.targets[index].date()), "feature_cutoff": str(windows.origins[index].date())})
        write_json(folder / f"lime_{index}.json", audit)
        explanation.save_to_file(str(folder / f"lime_{index}.html"))
        audits.append(audit)
        if first_explanation is None:
            first_explanation = explanation
            explanation.save_to_file(str(folder / "lime_local.html"))
            explanation.as_pyplot_figure()
            units = read_json(context["folder"] / "data_audit.json")["snapshot"]["units"]
            save_figure(folder / "lime_local", f"{context['folder'].name} | {context['name']} | {units} | LIME | {audit['target_date']}")
    repeat, repeat_audit = explain_lime(context["training"], context["model"].predict, windows.flat[context["indices"][0]], {**request, "seed": request["seed"] + 1})
    write_json(folder / "lime.json", {"primary": audits[0], "repeat_seed": repeat_audit, "all_dates": audits})
    return audits, [first_explanation, repeat]


def save_regime_drivers(attributions: np.ndarray, context: dict, folder: Path) -> None:
    from xai_finance.evaluate.regimes import regime_labels

    windows = context["windows"]
    regimes = regime_labels(windows.trailing_returns[context["indices"]], context["configuration"]["regime_threshold"])
    importance = np.abs(attributions.reshape(len(attributions), windows.x.shape[1], -1)).sum(axis=1)
    rankings = []
    for regime in np.unique(regimes):
        for name, score in zip(windows.feature_names, importance[regimes == regime].mean(axis=0)):
            rankings.append({"regime": regime, "feature": name, "mean_sum_abs_shap_over_lags": float(score), "explained_observations": int((regimes == regime).sum())})
    pd.DataFrame(rankings).to_csv(folder / "regime_drivers.csv", index=False)
