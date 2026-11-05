# شرح `src/xai_finance/pipelines/explain.py`

بصمة المصدر SHA-256: `62a6194d317aeac61fb9d69d7f99c26754c1a6bfb68f36a9855763bc07253ab1`.

شرح مسار توليد التفسير؛ لم يُنفذ في هذه الجلسة.

## الأسطر 1–7

```python
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
import torch
from threadpoolctl import threadpool_limits
```

Path وperf_counter معياريتان؛ NumPy وpandas وtorch وthreadpoolctl خارجية للمصفوفات والجداول وCUDA وحد الخيوط.

## الأسطر 9–15

```python
from xai_finance.explain.lime_explain import explain_lime
from xai_finance.explain.quality import attribution_stability, lime_weight_vector
from xai_finance.explain.shap_explain import explain_shap, shap_reconstruction
from xai_finance.pipelines.train import load_models, load_windows
from xai_finance.reports.plots import explanation_charts, save_figure
from xai_finance.seed import seed_experiment
from xai_finance.storage import read_json, write_json
```

استيرادات المشروع تربط مفسري LIME وSHAP واختبارات الجودة وتحميل النماذج والنوافذ والرسوم والبذور والتخزين.

## الأسطر 18–19

```python
def fixed_subset(indices: np.ndarray, count: int) -> np.ndarray:
    return indices[np.linspace(0, len(indices) - 1, min(count, len(indices)), dtype=int)]
```

fixed_subset تأخذ فهارس وعدداً وتستعمل linspace بفهرسة صحيحة لاختيار حتى count مواقع متباعدة من بداية إلى نهاية الفهارس؛ تعيد فهارس أصلية لا عينات عشوائية. عدد صفر أو فهارس فارغة يقود إلى مجموعة فارغة قد لا تحتملها المراحل اللاحقة.

## الأسطر 22–32

```python
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
```

explain_experiment تقرأ run.json وإعداداته وتضبط البذرة، ثم لكل أصل تحد الخيوط وتستدعي explain_asset وتفرغ cache عند توفر CUDA. بعد انتهاء جميع الأصول تحدث status وتكتب run.json؛ فشل مبكر يترك آثاراً جزئية.

## الأسطر 35–40

```python
def explain_asset(folder: Path, configuration: dict) -> None:
    windows = load_windows(folder)
    models = load_models(folder, configuration["device"])
    training = windows.flat[windows.partitions["train"]]
    background_indices = fixed_subset(windows.partitions["train"], configuration["background_samples"])
    background = windows.flat[background_indices]
```

explain_asset تحمل النوافذ والنماذج، وتحدد تدريباً مسطحاً كاملاً لمرجع LIME وخلفية SHAP من مجموعة ثابتة متباعدة داخل التدريب فقط. تقييد الخلفية يحمي من استخدام الاختبار كمرجع لكنه لا يضمن تمثيل التوزيع.

## الأسطر 41–47

```python
    for name, model in models.items():
        count = configuration["lstm_explain_samples"] if name == "LSTM" else configuration["explain_samples"]
        indices = fixed_subset(windows.partitions["test"], count)
        request = {"observations": windows.flat[indices], "names": windows.flat_names, "seed": configuration["seed"], "cycles": configuration["permutation_cycles"]}
        context = {"folder": folder, "name": name, "model": model, "windows": windows, "indices": indices, "background_indices": background_indices, "background": background, "training": training, "configuration": configuration}
        print(f"{folder.name}: explaining {name}, {len(indices)} fixed test observations", flush=True)
        explain_model(context, request)
```

تمر على النماذج الأربعة وتختار عدد تفسيرات LSTM أو غيره وتختار فهارس اختبار ثابتة، وتبني request وcontext بما في ذلك أسماء السمات والبذرة والميزانية، ثم تستدعي explain_model.

## الأسطر 50–60

```python
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
```

explain_model تنشئ مجلد النموذج وتحسب وتقيس تنبؤ نفس المشاهدات قبل التفسير، وتولد SHAP وتقيس زمنه ثم تتحقق من إعادة بناء التنبؤ؛ فشل assert يوقف المسار.

## الأسطر 61–66

```python
    np.savez_compressed(folder / "shap.npz", values=explanation.values, base_values=explanation.base_values, observations=request["observations"], indices=indices, feature_names=np.asarray(windows.flat_names))
    lime_audits, lime_explanations = explain_local_dates(context, folder)
    repeat_request = {**request, "seed": request["seed"] + 1, "observations": request["observations"][:1]}
    repeated = explain_shap(context["name"], model, context["background"], repeat_request)
    after = model.predict(request["observations"])
    np.testing.assert_array_equal(before, after)
```

تحفظ قيم SHAP والمرجع والمشاهدات والفهارس والأسماء في NPZ، وتولد LIME للتواريخ وتعيد SHAP لأول مشاهدة ببذرة أخرى؛ ثم تعيد التنبؤ وتطلب تطابقاً تاماً قبل وبعد. هذا الفحص لا يثبت ثبات كل الحالات.

## الأسطر 67–73

```python
    quality = {"shap_reconstruction": reconstruction, "prediction_unchanged_max_abs": float(np.max(np.abs(before - after))), "shap_elapsed_seconds": shap_seconds, "shap_samples": len(indices), "test_indices": indices.tolist(), "target_dates": [str(windows.targets[index].date()) for index in indices], "feature_cutoffs": [str(windows.origins[index].date()) for index in indices], "background_indices": context["background_indices"].tolist(), "background_max_target_date": str(windows.targets[context["background_indices"][-1]].date()), "shap_seed_stability": attribution_stability(explanation.values[0], repeated.values[0]), "lime_local": lime_audits, "lime_seed_stability": attribution_stability(lime_weight_vector(lime_explanations[0], len(windows.flat_names)), lime_weight_vector(lime_explanations[1], len(windows.flat_names))), "limitations": "Marginal masking and LIME neighborhoods can violate correlated technical-feature/time/OHLC constraints. Attributions are associations, not causality; global means cover only the declared subset."}
    quality["inference_elapsed_seconds_same_subset"] = inference_seconds
    quality["shap_overhead_ratio_same_subset"] = shap_seconds / max(inference_seconds, 1e-12)
    write_json(folder / "quality.json", quality)
    units = read_json(context["folder"] / "data_audit.json")["snapshot"]["units"]
    explanation_charts(explanation, folder, {"title": f"{context['folder'].name} | {context['name']} | {units}", "date": str(windows.targets[indices[0]].date()), "lookback": windows.x.shape[1], "features": windows.feature_names})
    save_regime_drivers(explanation.values, context, folder)
```

تجمع مقاييس إعادة البناء وأزمنة التفسير وتواريخ الهدف والأصل والخلفية واستقرار البذرة وقيود الترابط، وتضيف زمن inference ونسبة overhead مع مقام محمي من الصفر، وتكتب quality.json وترسم الآثار وتحسب محركات الحالات. مقارنة الزمن تعتمد نفس العينة وقياساً واحداً.

## الأسطر 76–83

```python
def explain_local_dates(context: dict, folder: Path) -> tuple[list[dict], list]:
    windows, configuration = context["windows"], context["configuration"]
    request = {"names": windows.flat_names, "seed": configuration["seed"], "samples": configuration["lime_samples"]}
    audits, first_explanation = [], None
    for index in context["indices"]:
        started = perf_counter()
        explanation, audit = explain_lime(context["training"], context["model"].predict, windows.flat[index], request)
        audit.update({"elapsed_seconds": perf_counter() - started, "target_date": str(windows.targets[index].date()), "feature_cutoff": str(windows.origins[index].date())})
```

explain_local_dates تنشئ طلب LIME بأسماء وبذرة وعدد عينات، وتكرر على فهارس الاختبار: تستدعي explain_lime على تدريب مسطح والتنبؤ والعينة، وتضيف الزمن وتاريخي الهدف والأصل.

## الأسطر 84–92

```python
        write_json(folder / f"lime_{index}.json", audit)
        explanation.save_to_file(str(folder / f"lime_{index}.html"))
        audits.append(audit)
        if first_explanation is None:
            first_explanation = explanation
            explanation.save_to_file(str(folder / "lime_local.html"))
            explanation.as_pyplot_figure()
            units = read_json(context["folder"] / "data_audit.json")["snapshot"]["units"]
            save_figure(folder / "lime_local", f"{context['folder'].name} | {context['name']} | {units} | LIME | {audit['target_date']}")
```

لكل عينة تكتب JSON وHTML وتضيف التدقيق للقائمة؛ لأول تفسير تحفظ أيضاً HTML وصورة من matplotlib بوحدة الأصل. هذه آثار كتابة ولا تنشأ عند مجرد قراءة الوثيقة.

## الأسطر 93–95

```python
    repeat, repeat_audit = explain_lime(context["training"], context["model"].predict, windows.flat[context["indices"][0]], {**request, "seed": request["seed"] + 1})
    write_json(folder / "lime.json", {"primary": audits[0], "repeat_seed": repeat_audit, "all_dates": audits})
    return audits, [first_explanation, repeat]
```

تعيد LIME لأول فهرس ببذرة مختلفة، وتكتب lime.json شاملاً التدقيق الأساسي والمكرر وجميع التواريخ، ثم تعيد قائمة التدقيق وتفسيرَي أول عينة. تفترض وجود فهرس اختبار واحد على الأقل.

## الأسطر 98–103

```python
def save_regime_drivers(attributions: np.ndarray, context: dict, folder: Path) -> None:
    from xai_finance.evaluate.regimes import regime_labels

    windows = context["windows"]
    regimes = regime_labels(windows.trailing_returns[context["indices"]], context["configuration"]["regime_threshold"])
    importance = np.abs(attributions.reshape(len(attributions), windows.x.shape[1], -1)).sum(axis=1)
```

save_regime_drivers تستورد regime_labels داخلياً، وتحسب حالات العينات المختارة من عوائدها الماضية وعتبة الإعداد، وتشكل قيم SHAP إلى عينة×زمن×سمة ثم تجمع القيم المطلقة عبر التأخيرات.

## الأسطر 104–108

```python
    rankings = []
    for regime in np.unique(regimes):
        for name, score in zip(windows.feature_names, importance[regimes == regime].mean(axis=0)):
            rankings.append({"regime": regime, "feature": name, "mean_sum_abs_shap_over_lags": float(score), "explained_observations": int((regimes == regime).sum())})
    pd.DataFrame(rankings).to_csv(folder / "regime_drivers.csv", index=False)
```

لكل حالة موجودة ولكل سمة تحسب متوسط مجموع القيم المطلقة وعدد المشاهدات المفسرة، وتكتب regime_drivers.csv. هو تلخيص لعينة التفسير المحدودة لا ترتيب سببي لكل السوق.
