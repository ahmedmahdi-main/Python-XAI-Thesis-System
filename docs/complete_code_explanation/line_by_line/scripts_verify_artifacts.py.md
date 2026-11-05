# شرح `scripts/verify_artifacts.py`

بصمة المصدر SHA-256: `a5debefd13f188f1fcc126b3b69427a7e98b275242a004e18a6c781e624392ff`.

لم تُنفذ إعادة التشغيل أو تدقيق النتائج في هذه الجلسة.

## الأسطر 1–14

```python
"""Independent original-unit and source-date audit of the current full experiment."""

from pathlib import Path

import numpy as np
import pandas as pd

from xai_finance.config import ROOT, load_config
from xai_finance.io.data_sources import load_snapshot
from xai_finance.pipelines.report import verify_saved_metrics
from xai_finance.pipelines.train import load_models, load_windows, resolve_run
from xai_finance.storage import read_json, sha256, write_json

MODELS = ["LinearRegression", "RandomForest", "GradientBoosting", "LSTM", "Persistence"]
```

توثيق واستيرادات المسار وNumPy وpandas ودوال الإعداد واللقطات والتقارير وتحميل النماذج والتخزين؛ MODELS تشمل أربعة نماذج وPersistence.

## الأسطر 17–24

```python
def verify_asset(folder: Path) -> dict:
    prices, manifest = load_snapshot(folder.name)
    windows = load_windows(folder)
    test = windows.partitions["test"]
    predictions = pd.read_csv(folder / "predictions.csv", parse_dates=["feature_cutoff", "target_date"])
    assert set(predictions.model) == set(MODELS)
    verify_saved_metrics(predictions, read_json(folder / "metrics.json"))
    labels = prices["adj_close"] if manifest["frequency"] == "daily" else prices["close"]
```

verify_asset تحمل اللقطة المحققة والنوافذ والتنبؤات وتتحقق من أسماء النماذج ومقاييسها وتختار الإغلاق المعدل لليومي والإغلاق للشهري.

## الأسطر 25–30

```python
    for name in MODELS:
        subset = predictions[predictions.model == name]
        assert pd.DatetimeIndex(subset.target_date).equals(windows.targets[test])
        assert (subset.feature_cutoff < subset.target_date).all()
        np.testing.assert_allclose(subset.actual, labels.loc[subset.target_date], atol=1e-8)
        np.testing.assert_allclose(subset.current_close, labels.loc[subset.feature_cutoff], atol=1e-8)
```

لكل نموذج تفحص تطابق تواريخ الأهداف مع الاختبار وترتيب الأصل قبل الهدف ومطابقة القيم الحالية واللاحقة مع اللقطة؛ لا يثبت ذلك تواريخ إتاحة البيانات المنقحة.

## الأسطر 31–39

```python
    models = load_models(folder, "cpu")
    for name, model in models.items():
        expected = predictions.loc[predictions.model == name, "predicted"].to_numpy()
        np.testing.assert_allclose(model.predict(windows.flat[test]), expected, rtol=1e-5, atol=1e-4)
        verify_explanation(folder / name / "explanations", windows, model)
    cutoff = models["LSTM"].scalers.fitted_target_cutoff
    assert cutoff == str(windows.targets[windows.partitions["train"][-1]].date())
    assert cutoff < str(windows.targets[test[0]].date())
    return {"asset": folder.name, "rows": manifest["rows"], "test_samples_per_model": len(test), "models": len(MODELS), "explanation_models": len(models), "status": "VERIFIED_FROM_ORIGINAL_SNAPSHOT_AND_RELOADED_CPU_MODELS"}
```

تعيد تحميل أربعة نماذج على CPU وتقارن تنبؤاتها بالمحفوظ ضمن tolerances وتفحص تفسيراتها، ثم تتحقق من تاريخ آخر هدف لتقييس LSTM وتعيد ملخص الأصل.

## الأسطر 42–50

```python
def verify_explanation(folder: Path, windows, model) -> None:
    quality = read_json(folder / "quality.json")
    assert quality["prediction_unchanged_max_abs"] == 0
    assert max(quality["background_indices"]) <= windows.partitions["train"][-1]
    with np.load(folder / "shap.npz", allow_pickle=False) as saved:
        predictions = model.predict(saved["observations"])
        np.testing.assert_allclose(np.asarray(saved["base_values"]).ravel() + saved["values"].sum(axis=1), predictions, rtol=1e-4, atol=1e-3)
        for index in saved["indices"]:
            assert index in windows.partitions["test"]
```

verify_explanation تقرأ جودة التفسير وتؤكد عدم تغير التنبؤ وأن الخلفية في التدريب، وتعيد بناء تنبؤ SHAP من base ومجموع القيم، وتتحقق من أن كل فهرس اختبار.

## الأسطر 51–56

```python
            local = read_json(folder / f"lime_{index}.json")
            assert local["target_date"] == str(windows.targets[index].date())
            assert local["feature_cutoff"] == str(windows.origins[index].date())
            assert np.isclose(local["absolute_local_error"], abs(local["model_prediction"] - local["local_surrogate_prediction"]))
    for name in ["shap_summary.png", "shap_waterfall.svg", "shap_dependence.png", "shap_force.html", "lime_local.png", "feature_time_heatmap.png", "global_importance.csv", "regime_drivers.csv"]:
        assert (folder / name).stat().st_size > 0
```

تقرأ LIME لنفس الفهرس وتتحقق من تواريخ الهدف والأصل وصيغة الخطأ المطلق، ثم من أحجام الرسوم؛ لا تختبر أن خطأ LIME صغير أو أن التفسير سببي.

## الأسطر 59–71

```python
def main() -> None:
    folder = resolve_run(load_config(ROOT / "configs/full_experiment.yaml"))
    metadata = read_json(folder / "run.json")
    assert metadata["source_sha256"] == sha256(ROOT / "docs/original_thesis.docx")
    assert metadata["provenance"] == "NEWLY_COMPUTED"
    assert read_json(ROOT / "docs/thesis_reported_reference.json")["provenance"] == "THESIS_REPORTED_NOT_REPRODUCED"
    for relative, expected in read_json(folder / "inventory.json").items():
        assert sha256(folder / relative) == expected, relative
    assets = [verify_asset(folder / asset) for asset in metadata["configuration"]["assets"]]
    write_json(folder / "verification.json", {"run_id": folder.name, "assets": assets, "status": "PASSED", "checks": "snapshot hashes, original dates/targets, metrics recomputation, common rows, CPU model reload, scaler cutoff, SHAP reconstruction/background, paired LIME dates, real chart files"})
    print("VERIFIED", folder.name)
    for audit in assets:
        print(audit)
```

main تحدد تشغيل full وتتحقق من بصمة الرسالة ومنشأ النتائج والمرجع التاريخي وبصمات الفهرس، ثم تدقق كل أصل وتكتب verification.json وتطبع. لم يُنفذ هنا؛ كتابته تغير ملف أثر.

## الأسطر 74–75

```python
if __name__ == "__main__":
    main()
```

حارس التشغيل المباشر.
