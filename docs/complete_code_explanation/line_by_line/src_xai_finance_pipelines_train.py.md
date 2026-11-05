# شرح `src/xai_finance/pipelines/train.py`

بصمة المصدر SHA-256: `a744962021fcb13f7f87caaf69f5f9520f8b66ce2f71522520b193c7bd660f76`.

المقاطع من المصدر الفعلي؛ لا تشغّل هذه الوثيقة التدريب أو تعدل الآثار. الأسطر الفارغة للتنسيق.

## الأسطر 1–13

```python
from datetime import datetime, timezone
import importlib.metadata
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
```

مكتبات قياسية للوقت والبيئة والمسارات والعمليات، وjoblib وNumPy وpandas وthreadpoolctl للحفظ والحساب والجداول وحد الخيوط.

## الأسطر 15–25

```python
from xai_finance.config import ROOT
from xai_finance.data.features import features
from xai_finance.data.windows import WindowDataset, build_windows
from xai_finance.evaluate.metrics import forecast_metrics
from xai_finance.evaluate.regimes import regime_labels, regime_metrics
from xai_finance.io.data_sources import load_snapshot
from xai_finance.models.baselines import persistence
from xai_finance.models.lstm_model import fit_lstm, load_lstm
from xai_finance.models.sklearn_models import candidates, fit_candidates
from xai_finance.seed import seed_experiment
from xai_finance.storage import read_json, sha256, write_json
```

يربط ROOT وبناء السمات والنوافذ والمقاييس والحالات واللقطات وPersistence وLSTM ونماذج sklearn والبذرة والتخزين؛ هذه تبعيات داخلية لمسار التجربة.

## الأسطر 28–31

```python
def software_environment() -> dict:
    packages = {name: importlib.metadata.version(name) for name in ["numpy", "pandas", "scikit-learn", "torch", "shap", "lime", "yfinance", "streamlit"]}
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], capture_output=True, text=True) if shutil.which("nvidia-smi") else None
    return {"python": sys.version, "executable": sys.executable, "platform": platform.platform(), "packages": packages, "gpu": gpu.stdout.strip() if gpu else "nvidia-smi unavailable", "pythonhashseed": os.environ.get("PYTHONHASHSEED", "not set at startup; numerical seeds still fixed")}
```

software_environment تجمع إصدارات الحزم ونسخة Python والمنصة ومعلومات nvidia-smi إن كان موجوداً ومتغير PYTHONHASHSEED؛ تعيد قاموساً وقد تفشل إذا تعذر استعلام إصدار حزمة.

## الأسطر 34–39

```python
def train_experiment(configuration: dict) -> Path:
    run_id = configuration["name"] + "_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder = ROOT / "artifacts/runs" / run_id
    folder.mkdir(parents=True, exist_ok=False)
    metadata = {"run_id": run_id, "status": "TRAINING", "provenance": "NEWLY_COMPUTED", "created_utc": datetime.now(timezone.utc).isoformat(), "configuration": configuration, "environment": software_environment(), "source_sha256": sha256(ROOT / "docs/original_thesis.docx"), "assets_completed": []}
    write_json(folder / "run.json", metadata)
```

train_experiment تبني run_id من اسم الإعداد ووقت UTC، وتنشئ مجلد تشغيل جديداً مع exist_ok=False، وتكتب run.json الأولي مع البيئة وبصمة ملف الرسالة وحالة TRAINING.

## الأسطر 40–49

```python
    for asset in configuration["assets"]:
        with threadpool_limits(limits=4):
            train_asset(asset, configuration, folder / asset)
        metadata["assets_completed"].append(asset)
        write_json(folder / "run.json", metadata)
    metadata["status"] = "TRAINED_ALL_FOUR_MODELS"
    write_json(folder / "run.json", metadata)
    write_json(ROOT / f"artifacts/latest_{configuration['name']}.json", {"run_id": run_id})
    print(f"Completed training run: {run_id}", flush=True)
    return folder
```

لكل أصل تحد الخيوط بأربعة وتستدعي train_asset ثم تحدث قائمة الإنجاز والملف. بعد اكتمال الكل تحدث الحالة وتكتب مؤشر latest وتعيد مسار التشغيل؛ فشل أثناء الحلقة قد يترك تشغيلًا غير مكتمل دون تحديث المؤشر النهائي.

## الأسطر 52–54

```python
def save_windows(folder: Path, windows: WindowDataset) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(folder / "windows.npz", x=windows.x, y=windows.y, origins=windows.origins.asi8, targets=windows.targets.asi8, current=windows.current_close, trailing=windows.trailing_returns, names=np.asarray(windows.feature_names), **windows.partitions)
```

save_windows تنشئ مجلد الأصل وتحفظ مضغوطاً x وy والتواريخ بوحدة asi8 والقيم والأسماء والتقسيمات في windows.npz؛ هذه كتابة أثر عند التدريب.

## الأسطر 57–59

```python
def load_windows(folder: Path) -> WindowDataset:
    with np.load(folder / "windows.npz", allow_pickle=False) as saved:
        return WindowDataset(saved["x"], saved["y"], pd.DatetimeIndex(saved["origins"]), pd.DatetimeIndex(saved["targets"]), saved["current"], saved["trailing"], saved["names"].tolist(), {partition: saved[partition] for partition in ["train", "validation", "test"]})
```

load_windows تقرأ NPZ دون pickle وتعيد WindowDataset مع تحويل التواريخ وحقول التقسيم؛ تعتمد أسماء وأشكال الحقول المحفوظة.

## الأسطر 62–63

```python
def split_manifest(windows: WindowDataset) -> dict:
    return {partition: {"n": len(indices), "origin_start": str(windows.origins[indices[0]].date()), "origin_end": str(windows.origins[indices[-1]].date()), "target_start": str(windows.targets[indices[0]].date()), "target_end": str(windows.targets[indices[-1]].date())} for partition, indices in windows.partitions.items()}
```

split_manifest تعيد لكل قسم العدد وحدود تاريخ الأصل والهدف من أول فهرس وآخره؛ تفترض الأقسام غير فارغة ومرتبة.

## الأسطر 66–74

```python
def train_asset(asset: str, configuration: dict, folder: Path) -> None:
    seed_experiment(configuration["seed"])
    prices, manifest = load_snapshot(asset)
    engineered = features(prices, manifest["frequency"])
    lookback = configuration["monthly_lookback"] if manifest["frequency"] == "monthly" else configuration["lookback"]
    windows = build_windows(engineered, lookback)
    save_windows(folder, windows)
    engineered.to_csv(folder / "features.csv", index_label="feature_cutoff")
    write_json(folder / "data_audit.json", {"snapshot": manifest, "split": split_manifest(windows), "lookback": lookback, "features": windows.feature_names, "information_set": "All four models use identical flattened or recurrent full historical windows", "feature_rows_dropped_warmup": len(prices) - len(engineered), "target": "next observed adjusted close" if manifest["frequency"] == "daily" else "next monthly observed index; retrospective/revised series, not publication-time forecast"})
```

train_asset تثبت البذرة، تتحقق من لقطة الأصل وتحسب السمات وتختار lookback حسب التردد وتبني وتحفظ النوافذ والسمات وتقرير المصدر والتقسيم والهدف. هدف اليوم التالي هو الرصد التالي وليس بالضرورة اليوم التقويمي التالي.

## الأسطر 75–83

```python
    selected_models, training_audits = {}, {}
    for model_name, estimators in candidates(configuration).items():
        print(f"{asset}: fitting {model_name} on training only", flush=True)
        selected_models[model_name], training_audits[model_name] = fit_candidates(estimators, windows)
        joblib.dump(selected_models[model_name], folder / f"{model_name}.joblib")
    print(f"{asset}: baseline training complete; starting LSTM", flush=True)
    selected_models["LSTM"], training_audits["LSTM"] = fit_lstm(windows, {**configuration, "effective_lookback": lookback}, folder / "LSTM")
    joblib.dump(selected_models["LSTM"].scalers, folder / "LSTM/scalers.joblib")
    write_json(folder / "training.json", training_audits)
```

تجهز المرشحين وتلائمهم وتختار على التحقق وتحفظ كل نموذج joblib، ثم تدرب LSTM وتحفظ scaler وسجل التدريب؛ كل ذلك يحدث فقط عند تشغيل التدريب لا عند قراءة التوثيق.

## الأسطر 84–86

```python
    evaluate_asset(asset, windows, selected_models, folder, configuration)
    verify_reload(folder, selected_models, windows)
    save_next_forecasts(selected_models, engineered, folder, lookback)
```

تستدعي التقييم، وفحص تحميل CPU، ثم حفظ توقع الرصد التالي للّقطة. ترتيبها يعني أن فشل فحص التحميل يمنع إنشاء توقع لاحق في ذلك التنفيذ.

## الأسطر 89–93

```python
def evaluate_asset(asset: str, windows: WindowDataset, models: dict, folder: Path, configuration: dict) -> None:
    test = windows.partitions["test"]
    rows, metric_rows = [], []
    predictions = {name: model.predict(windows.flat[test]) for name, model in models.items()}
    predictions["Persistence"] = persistence(windows.current_close[test])
```

evaluate_asset تحدد test وتتنبأ جميع النماذج بالنوافذ المسطحة؛ يعيد LSTMPredictor تشكيلها داخلياً. تضيف Persistence كقيمة الإغلاق الحالي، دون تدريب مرجعي.

## الأسطر 94–102

```python
    for model_name, predicted in predictions.items():
        model_folder = folder / model_name
        model_folder.mkdir(exist_ok=True)
        table = pd.DataFrame({"asset": asset, "model": model_name, "feature_cutoff": windows.origins[test], "target_date": windows.targets[test], "actual": windows.y[test], "predicted": predicted, "current_close": windows.current_close[test], "regime": regime_labels(windows.trailing_returns[test], configuration["regime_threshold"])})
        table.to_csv(model_folder / "predictions.csv", index=False)
        metrics = {"asset": asset, "model": model_name, "provenance": "NEWLY_COMPUTED", **forecast_metrics(windows.y[test], predicted, windows.current_close[test])}
        write_json(model_folder / "metrics.json", metrics)
        metric_rows.append(metrics)
        rows.append(table)
```

لكل نموذج تنشئ مجلداً وجدول تواريخ وقيم وحالات، وتكتب تنبؤات الاختبار وتحسب forecast_metrics وتكتب JSON، ثم تضيف البيانات إلى القوائم. الإعداد يحدد عتبة الحالة.

## الأسطر 103–107

```python
    combined = pd.concat(rows, ignore_index=True)
    combined.to_csv(folder / "predictions.csv", index=False)
    write_json(folder / "metrics.json", metric_rows)
    write_json(folder / "regimes.json", regime_metrics(combined))
    print(pd.DataFrame(metric_rows)[["asset", "model", "mae", "rmse", "r2"]].to_string(index=False), flush=True)
```

تجمع الجداول وتكتب predictions.csv وmetrics.json وregimes.json ثم تطبع مختصر الأخطاء. هذه النتائج بوحدات الهدف الأصلية بعد عكس معيار LSTM.

## الأسطر 110–114

```python
def load_models(folder: Path, device: str = "auto") -> dict:
    models = {name: joblib.load(folder / f"{name}.joblib") for name in ["LinearRegression", "RandomForest", "GradientBoosting"]}
    models["RandomForest"].set_params(n_jobs=1)
    models["LSTM"] = load_lstm(folder / "LSTM", joblib.load(folder / "LSTM/scalers.joblib"), device)
    return models
```

load_models تقرأ نماذج joblib الثلاثة، تجعل الغابة متسلسلة، وتحمل LSTM ومعاييره للجهاز المطلوب؛ تعيد قاموساً. تحميل pickle/joblib يتطلب آثاراً موثوقة.

## الأسطر 117–123

```python
def verify_reload(folder: Path, trained: dict, windows: WindowDataset) -> None:
    fixture = windows.flat[windows.partitions["test"][:5]]
    reloaded = load_models(folder, "cpu")
    errors = {name: float(np.max(np.abs(model.predict(fixture) - reloaded[name].predict(fixture)))) for name, model in trained.items()}
    for name, difference in errors.items():
        np.testing.assert_allclose(trained[name].predict(fixture), reloaded[name].predict(fixture), rtol=1e-5, atol=1e-4)
    write_json(folder / "reload_check.json", {"cpu_reload_max_abs_error": errors, "rtol": 1e-5, "atol": 1e-4})
```

verify_reload تقارن تنبؤات أول خمس نوافذ اختبار بين النموذج الموجود وإعادة تحميله على CPU، وتسجل أقصى فرق وتفرض allclose بـ rtol=1e-5 وatol=1e-4. الفحص لهذه العينة وليس إثبات تطابق جميع البيانات.

## الأسطر 126–129

```python
def save_next_forecasts(models: dict, engineered: pd.DataFrame, folder: Path, lookback: int) -> None:
    window = engineered.iloc[-lookback:].to_numpy().reshape(1, -1)
    forecasts = {name: float(model.predict(window)[0]) for name, model in models.items()}
    write_json(folder / "next_forecast.json", {"feature_cutoff": str(engineered.index[-1].date()), "status": "UNVERIFIED_NEXT_OBSERVATION_AFTER_SNAPSHOT_NOT_A_CURRENT_LIVE_FORECAST", "predictions": forecasts})
```

save_next_forecasts تسطح أحدث lookback صفوف سمات وتطلب توقع كل نموذج ثم تكتب التاريخ والحالة التي تنفي التحقق أو الآنية. لا يوجد هدف مرصود هنا للمقارنة.

## الأسطر 132–134

```python
def resolve_run(configuration: dict) -> Path:
    pointer = read_json(ROOT / f"artifacts/latest_{configuration['name']}.json")
    return ROOT / "artifacts/runs" / pointer["run_id"]
```

resolve_run تقرأ مؤشر latest للتكوين وتعيد مجلد التشغيل المشار إليه؛ لا تتحقق هنا أن المجلد أو كل ملفاته موجودة.
