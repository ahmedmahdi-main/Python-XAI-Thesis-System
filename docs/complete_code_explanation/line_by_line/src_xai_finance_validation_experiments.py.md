# شرح `src/xai_finance/validation/experiments.py`

بصمة المصدر SHA-256: `ceb4c3e23ea536f71e455a295c9c0f9bed84d65e74897c505d0b3895fedb01ec`.

المقاطع من المصدر؛ التفسير مراجعة يدوية دون تشغيل التجارب.

## الأسطر 1–17

```python
from dataclasses import replace
import gc
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
from threadpoolctl import threadpool_limits

from xai_finance.models.lstm_model import fit_lstm
from xai_finance.models.sklearn_models import candidates, fit_candidates
from xai_finance.pipelines.train import load_windows, software_environment, split_manifest, verify_reload
from xai_finance.seed import seed_experiment
from xai_finance.storage import read_json, sha256, write_json
from xai_finance.validation.design import implied_prices, naive_predictions, transformed_windows, walk_forward_partitions
from xai_finance.validation.statistics import evaluation_metrics
```

يستورد replace وgc وPath القياسية، ومكتبات حفظ وعدد وحساب وTorch وخيوط خارجية، ودوال نماذج وتكوين وبيانات وتقييم داخلية.

## الأسطر 20–28

```python
def fit_models(windows, configuration: dict, folder: Path) -> tuple[dict, dict]:
    models, audits = {}, {}
    for name, estimators in candidates(configuration).items():
        print(f"{folder.name}: fitting {name}", flush=True)
        models[name], audits[name] = fit_candidates(estimators, windows)
        joblib.dump(models[name], folder / f"{name}.joblib")
    models["LSTM"], audits["LSTM"] = fit_lstm(windows, configuration, folder / "LSTM")
    joblib.dump(models["LSTM"].scalers, folder / "LSTM/scalers.joblib")
    return models, audits
```

fit_models تلائم مرشحي sklearn على النوافذ وتعتمد تحقق الاختيار ثم تحفظهم، وتدرب LSTM وتحفظ معاييره، وتعيد النماذج وسجلات التدريب. هذه الدالة تدرب وتكتب آثاراً عند استدعائها؛ لم تُنفذ هنا.

## الأسطر 31–39

```python
def predictions_table(windows, specification: dict, models: dict) -> pd.DataFrame:
    test, target = windows.partitions["test"], specification["target"]
    predictions = {name: model.predict(windows.flat[test]) for name, model in models.items()}
    predictions.update(naive_predictions(windows, target))
    transformed = transformed_windows(windows, target)
    tables = []
    for name, predicted in predictions.items():
        tables.append(pd.DataFrame({**specification, "model": name, "feature_cutoff": windows.origins[test], "target_date": windows.targets[test], "current_price": windows.current_close[test], "actual_price": windows.y[test], "predicted_price": implied_prices(predicted, windows.current_close[test], target), "actual_target": transformed.y[test], "predicted_target": predicted}))
    return pd.concat(tables, ignore_index=True)
```

predictions_table تحصل على تنبؤات النماذج وأربعة مراجع naive وتحوّل الهدف، وتنشئ لكل نموذج صفوف بيانات تتضمن تواريخ وأسعاراً وهدفاً حقيقياً ومتوقعاً، وتعيد جدولاً موحداً. implied_prices يحول توقع الهدف إلى سعر.

## الأسطر 42–46

```python
def job_configuration(protocol: dict, specification: dict) -> dict:
    configuration = {**protocol["lstm"], "seed": protocol["seed"], "trees": 100, "search": True}
    if specification["design"] == "walk_forward":
        configuration["epochs"] = protocol["walk_forward"]["lstm_epochs"]
    return configuration
```

job_configuration تدمج إعداد LSTM مع البذرة و100 شجرة والبحث، وتغير حد epochs عند walk_forward حسب البروتوكول؛ تعيد القاموس.

## الأسطر 49–56

```python
def experiment_job(windows, specification: dict, context: dict) -> None:
    folder = context["destination"] / "experiments" / specification["design"] / specification["target"] / f"{specification['asset']}_fold{specification['fold']}"
    if (folder / "completion.json").exists():
        previous = read_json(folder / "completion.json")
        for name, digest in previous["files"].items():
            assert sha256(folder / name) == digest, f"Completed job changed: {folder / name}"
        print(f"Verified completed job: {folder}", flush=True)
        return
```

experiment_job تحدد مجلد التصميم والهدف والأصل والطية؛ إذا وُجد completion.json تتحقق من بصمات الملفات المذكورة وتعود. الفحص لا يتأكد وحده من غياب ملفات إضافية.

## الأسطر 57–65

```python
    folder.mkdir(parents=True, exist_ok=False)
    seed_experiment(context["protocol"]["seed"])
    target_windows = transformed_windows(windows, specification["target"])
    configuration = job_configuration(context["protocol"], specification)
    write_json(folder / "design.json", {**specification, "configuration": configuration, "split": split_manifest(windows), "target_definition": context["protocol"]["targets"][specification["target"]], "input_windows_source": str(context["original"] / specification["asset"] / "windows.npz"), "input_windows_sha256": sha256(context["original"] / specification["asset"] / "windows.npz")})
    np.savez_compressed(folder / "target_and_partitions.npz", y=target_windows.y, origins=windows.origins.asi8, targets=windows.targets.asi8, **windows.partitions)
    models, training = fit_models(target_windows, configuration, folder)
    write_json(folder / "training.json", training)
    verify_reload(folder, models, target_windows)
```

لعمل جديد تنشئ المجلد دون استبدال وتضبط البذرة وتحول الهدف وتكتب التصميم وبصمة نوافذ المصدر وتحفظ الأهداف والتقسيمات، ثم تدرب وتحفظ وتسجل وتتحقق من إعادة التحميل. هذه عمليات تعديل آثار وتجارب فعلية إن شغلت.

## الأسطر 66–75

```python
    table = predictions_table(windows, specification, models)
    table.to_csv(folder / "predictions.csv", index=False)
    metric_rows = [{**specification, "model": name, **evaluation_metrics(group)} for name, group in table.groupby("model", sort=False)]
    write_json(folder / "metrics.json", metric_rows)
    write_json(folder / "completion.json", {"files": {str(path.relative_to(folder)): sha256(path) for path in folder.rglob("*") if path.is_file()}, "status": "EXECUTED_AND_CPU_RELOAD_VERIFIED"})
    print(pd.DataFrame(metric_rows)[["asset", "model", "rmse", "rmse_ratio_vs_zero", "direction_accuracy"]].to_string(index=False), flush=True)
    del models
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
```

تكتب تنبؤات ومقاييس ونهاية العمل مع بصمات الملفات ثم تطبع النتائج وتحرر النماذج وcache CUDA عند توفره. تحسب المقاييس على الأقسام المحددة في النوافذ.

## الأسطر 78–89

```python
def run_experiments(context: dict) -> None:
    protocol = context["protocol"]
    write_json(context["destination"] / "environment.json", {**software_environment(), "torch_cuda_available": torch.cuda.is_available(), "torch_cuda_version": torch.version.cuda, "cudnn_version": torch.backends.cudnn.version(), "protocol_sha256": sha256(context["destination"] / "protocol.json")})
    with threadpool_limits(limits=4):
        for target, assets in protocol["fixed_split"].items():
            for asset in assets:
                windows = load_windows(context["original"] / asset)
                experiment_job(windows, {"asset": asset, "target": target, "design": "fixed_split", "fold": 0}, context)
        for asset in protocol["walk_forward"]["assets"]:
            windows = load_windows(context["original"] / asset)
            for fold, partition in enumerate(walk_forward_partitions(windows, protocol["walk_forward"]["folds"]), 1):
                experiment_job(replace(windows, partitions=partition), {"asset": asset, "target": "price_change", "design": "walk_forward", "fold": fold}, context)
```

run_experiments تكتب معلومات البيئة وبصمة البروتوكول وتحد الخيوط، ثم تشغل التجارب الثابتة للأهداف والأصول المحددة وwalk-forward لأصوله مع استبدال التقسيمات لكل طية. يحدد البروتوكول النطاق؛ لا يجوز اعتبار النتائج تجارب جديدة مستقلة تماماً عن الاختبار المعروف.

## الأسطر 92–102

```python
def aggregate_experiments(destination: Path) -> None:
    tables = [pd.read_csv(path) for path in sorted((destination / "experiments").rglob("predictions.csv"))]
    predictions = pd.concat(tables, ignore_index=True)
    predictions.to_csv(destination / "new_predictions.csv", index=False)
    metric_rows = []
    for keys, group in predictions.groupby(["design", "target", "asset", "model"], sort=False):
        assert not group.target_date.duplicated().any()
        group = group.sort_values("target_date")
        metric_rows.append({**dict(zip(["design", "target", "asset", "model"], keys)), **evaluation_metrics(group)})
    pd.DataFrame(metric_rows).to_csv(destination / "new_metrics.csv", index=False)
    write_json(destination / "new_metrics.json", metric_rows)
```

aggregate_experiments تقرأ كل predictions.csv في مجلد التجارب وتجمعها، وتتحقق من عدم تكرار تاريخ الهدف داخل كل تصميم وهدف وأصل ونموذج، وترتب التاريخ وتحسب مقاييس مجمعة وتكتب CSV وJSON. تفترض وجود ملفات ومحاذاة صحيحة.
