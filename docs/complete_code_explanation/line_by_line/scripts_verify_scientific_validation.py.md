# شرح `scripts/verify_scientific_validation.py`

بصمة المصدر SHA-256: `3e2f23a91b3db309dfaef515c7df378810965f9069d868c9e894abbd97eca36f`.

لم تُنفذ إعادة التشغيل أو تدقيق النتائج في هذه الجلسة.

## الأسطر 1–15

```python
"""Read-only replay of every additional prediction plus frozen-file preservation."""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from xai_finance.config import ROOT
from xai_finance.pipelines.train import load_models, load_windows
from xai_finance.seed import seed_experiment
from xai_finance.storage import read_json, sha256, write_json
from xai_finance.validation.design import implied_prices, naive_predictions, target_values
from xai_finance.validation.statistics import evaluation_metrics
```

توثيق واستيرادات argparse وreplace والوقت والمسارات وNumPy وpandas ووظائف المشروع للتحميل والتنبؤ والتقييم والهاش.

## الأسطر 18–28

```python
def replay_job(folder: Path, original: Path) -> dict:
    design = read_json(folder / "design.json")
    windows = load_windows(original / design["asset"])
    with np.load(folder / "target_and_partitions.npz", allow_pickle=False) as saved:
        windows = replace(windows, partitions={name: saved[name].copy() for name in ["train", "validation", "test"]})
        np.testing.assert_array_equal(saved["y"], target_values(windows, design["target"]))
    table = pd.read_csv(folder / "predictions.csv", float_precision="round_trip")
    test = windows.partitions["test"]
    models = load_models(folder, "cpu")
    expected = {name: model.predict(windows.flat[test]) for name, model in models.items()}
    expected.update(naive_predictions(windows, design["target"]))
```

replay_job تحمل التصميم والنوافذ وتستبدل التقسيمات من NPZ دون pickle، وتفحص الهدف المحول وتقرأ الجدول وتحمل نماذج CPU وتحسب توقعات النماذج والمراجع.

## الأسطر 29–39

```python
    maximum_error = {}
    for name, group in table.groupby("model", sort=False):
        np.testing.assert_array_equal(pd.to_datetime(group.target_date), windows.targets[test])
        np.testing.assert_array_equal(pd.to_datetime(group.feature_cutoff), windows.origins[test])
        np.testing.assert_allclose(group.actual_price, windows.y[test], rtol=1e-12)
        if name == "LSTM":
            # CPU and CUDA accumulate FP32 recurrent operations differently; compare in training standard-deviation units.
            absolute_tolerance = 8 * np.finfo(np.float32).eps * models[name].scalers.target.scale_[0]
            np.testing.assert_allclose(group.predicted_target, expected[name], rtol=0, atol=absolute_tolerance)
        else:
            np.testing.assert_allclose(group.predicted_target, expected[name], rtol=1e-9, atol=1e-9)
```

لكل نموذج تتحقق من تواريخ الهدف والأصل والقيم الفعلية، وتقارن الهدف المتوقع: LSTM بسماح مطلق يساوي ثمانية أضعاف epsilon لـ float32 مضروباً في مقياس هدف التدريب، والآخرون بسماح 1e-9. التسامح يعالج فروق الأجهزة لا يضمن تماثل كل البيئات.

## الأسطر 40–46

```python
        native_target = group.predicted_target.to_numpy().astype(expected[name].dtype)
        np.testing.assert_allclose(group.predicted_price, implied_prices(native_target, group.current_price.to_numpy(), design["target"]), rtol=1e-12)
        maximum_error[name] = float(np.max(np.abs(group.predicted_target - expected[name])))
    completion = read_json(folder / "completion.json")
    for name, digest in completion["files"].items():
        assert sha256(folder / name) == digest
    return {"job": str(folder.relative_to(original.parent.parent.parent)), "rows_replayed": len(table), "cpu_target_prediction_max_abs_error": maximum_error}
```

تحول التوقع المحفوظ إلى dtype التنبؤ الأصلي قبل إعادة تركيب السعر لتكرار دقة الحساب، وتحسب أقصى اختلاف وتتحقق من بصمات completion وتعيد ملخص المهمة.

## الأسطر 49–63

```python
def verify_aggregate(destination: Path) -> dict:
    table = pd.read_csv(destination / "new_predictions.csv")
    metrics = read_json(destination / "new_metrics.json")
    for row in metrics:
        subset = table
        for key in ["design", "target", "asset", "model"]:
            subset = subset[subset[key] == row[key]]
        assert not subset.target_date.duplicated().any()
        recomputed = evaluation_metrics(subset.sort_values("target_date"))
        for name, value in recomputed.items():
            if isinstance(value, float):
                np.testing.assert_allclose(value, row[name], rtol=1e-8, atol=1e-8)
            else:
                assert value == row[name]
    return {"aggregate_rows": len(table), "aggregate_metric_rows": len(metrics), "all_metrics_recomputed_from_serialized_predictions": True}
```

verify_aggregate تقرأ التنبؤات والمقاييس المجمعة، وترشح لكل مجموعة وتمنع تكرار تاريخ الهدف ثم تعيد حساب evaluation_metrics وتقارن جميع النتائج، وتعيد عدد الصفوف. bootstrap ضمن evaluation_metrics يعاد حسابه عند التشغيل.

## الأسطر 66–74

```python
def preservation_receipt(destination: Path) -> dict:
    inventory = read_json(destination / "preservation_before.json")
    mismatches = []
    for relative, previous in inventory.items():
        path = ROOT / relative
        if not path.exists() or path.stat().st_size != previous["bytes"] or sha256(path) != previous["sha256"]:
            mismatches.append(relative)
    assert not mismatches, f"Protected files changed: {mismatches}"
    return {"protected_files": len(inventory), "mismatches": mismatches, "before_inventory_sha256": sha256(destination / "preservation_before.json"), "offline_zip_sha256": sha256(ROOT / "backups/defense_full_20261021T040901084647Z.zip")}
```

preservation_receipt تقارن حجم وبصمة الملفات مع سجل ما قبل التحقق وتفرض عدم تغيرها، وتعيد العدد وبصمتي السجل وZIP؛ تعتمد على شمول السجل وصحته.

## الأسطر 77–89

```python
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    arguments = parser.parse_args()
    destination = arguments.folder.resolve()
    seed_experiment(42)
    original = ROOT / "artifacts/runs" / read_json(destination / "protocol.json")["original_run"]
    jobs = sorted((destination / "experiments").rglob("completion.json"))
    assert len(jobs) == 15, f"Expected 15 executed jobs; found {len(jobs)}"
    replay = [replay_job(path.parent, original) for path in jobs]
    receipt = {"verified_utc": datetime.now(timezone.utc).isoformat(), "jobs": replay, "cpu_lstm_tolerance_training_std_units": float(8 * np.finfo(np.float32).eps), **verify_aggregate(destination), "preservation": preservation_receipt(destination)}
    write_json(destination / "verification.json", receipt)
    print(f"Verified {len(replay)} jobs, {receipt['aggregate_rows']} serialized predictions and {receipt['preservation']['protected_files']} unchanged protected files")
```

main تقرأ الوجهة وتضبط البذرة وتحدد الأصل وتؤكد وجود 15 مهمة، ثم تعيد تشغيلها وتدقق التجميع والمحافظة وتكتب verification.json وتطبع. ليست قراءة خالصة لأن الإيصال يكتب؛ لم يُنفذ هنا.

## الأسطر 92–93

```python
if __name__ == "__main__":
    main()
```

حارس التنفيذ المباشر.
