# شرح `src/xai_finance/validation/audit.py`

بصمة المصدر SHA-256: `326bd2c60ea2d6853a41ed016821143a263a96f9d7524a3954907297aaa5a4d2`.

المقاطع من المصدر؛ التفسير مراجعة يدوية دون تشغيل التجارب.

## الأسطر 1–11

```python
import joblib
import numpy as np
import pandas as pd

from xai_finance.data.features import features
from xai_finance.data.preprocess import fit_training_scalers
from xai_finance.data.windows import build_windows
from xai_finance.evaluate.metrics import forecast_metrics
from xai_finance.io.data_sources import load_snapshot
from xai_finance.pipelines.train import load_models, load_windows, split_manifest
from xai_finance.storage import write_json
```

مكتبات joblib وNumPy وpandas خارجية؛ يستورد المصدر بناء السمات والمعايير والنوافذ والمقاييس واللقطات وتحميل النماذج والتخزين من المشروع.

## الأسطر 14–19

```python
def causal_feature_check(prices: pd.DataFrame, frequency: str) -> dict:
    cutoff = int(0.8 * len(prices))
    prefix = features(prices.iloc[:cutoff], frequency)
    complete = features(prices, frequency).loc[prefix.index]
    np.testing.assert_allclose(prefix, complete, rtol=0, atol=0)
    return {"prefix_rows": len(prefix), "future_deletion_max_feature_error": float(np.max(np.abs(prefix.to_numpy() - complete.to_numpy())))}
```

causal_feature_check تعيد حساب السمات على أول 80% من الأسعار ثم على كامل السلسلة وتقارن الصفوف المشتركة بتسامح صفري، وتعيد أكبر فرق. يحسن هذا فحص الاعتماد على مستقبل الصفوف، لكنه لا يثبت توافر اللقطة المعدلة تاريخياً أو كل مظاهر التسرب.

## الأسطر 22–30

```python
def alignment_check(windows, prices, manifest) -> dict:
    next_dates = prices.index[prices.index.get_indexer(windows.origins) + 1]
    assert windows.targets.equals(next_dates)
    close = "adj_close" if manifest["frequency"] == "daily" else "close"
    np.testing.assert_array_equal(windows.y, prices.loc[next_dates, close])
    np.testing.assert_array_equal(windows.current_close, prices.loc[windows.origins, close])
    for earlier, later in [("train", "validation"), ("validation", "test")]:
        assert windows.targets[windows.partitions[earlier][-1]] <= windows.origins[windows.partitions[later][0]]
    return {"all_labels_equal_next_raw_observation": True, "partition_label_availability_verified": True, "split": split_manifest(windows)}
```

alignment_check تحدد تاريخ الرصد الخام التالي لكل أصل، وتتحقق من تطابقه مع الهدف وقيم الإغلاق الحالي واللاحق، ومن إتاحة آخر تسمية قسم سابق عند أول أصل القسم التالي؛ تعيد تقرير التقسيم. تستخدم assert وقد تُزال مع تشغيل Python المحسن.

## الأسطر 33–42

```python
def scaler_check(windows, folder) -> dict:
    saved = joblib.load(folder / "LSTM/scalers.joblib")
    recalculated = fit_training_scalers(windows)
    for name in ["inputs", "target"]:
        for attribute in ["mean_", "scale_", "var_"]:
            np.testing.assert_array_equal(getattr(getattr(saved, name), attribute), getattr(getattr(recalculated, name), attribute))
    restored = saved.inverse_target(saved.target.transform(windows.y[:, None]))
    np.testing.assert_allclose(restored, windows.y, rtol=1e-12, atol=1e-12)
    test_scaled = saved.target.transform(windows.y[windows.partitions["test"], None]).ravel()
    return {"saved_scalers_match_training_only_recalculation": True, "inverse_max_abs_error": float(np.max(np.abs(restored - windows.y))), "test_standardized_target_min": float(test_scaled.min()), "test_standardized_target_max": float(test_scaled.max())}
```

scaler_check تحمل معايير LSTM وتعيد ملاءمتها على التدريب للتحقق من mean وscale وvar، وتفحص عكس المعيار وتحسب مدى أهداف الاختبار المعيارية. هذا فحص للمعايير وليس إعادة تدريب النموذج؛ تحميل joblib يفترض ملفاً موثوقاً.

## الأسطر 45–52

```python
def distribution_shift(windows, models) -> dict:
    train, test = windows.partitions["train"], windows.partitions["test"]
    minimum, maximum = windows.y[train].min(), windows.y[train].max()
    outside = (windows.y[test] < minimum) | (windows.y[test] > maximum)
    inputs = windows.flat
    train_min, train_max = inputs[train].min(axis=0), inputs[train].max(axis=0)
    clipped = np.clip(inputs[test], train_min, train_max)
    audit = {"train_price_min": float(minimum), "train_price_max": float(maximum), "test_price_min": float(windows.y[test].min()), "test_price_max": float(windows.y[test].max()), "test_price_outside_train_fraction": float(outside.mean()), "test_feature_cells_outside_train_fraction": float(np.mean(inputs[test] != clipped))}
```

distribution_shift تحدد مجال أهداف التدريب ونسبة أهداف الاختبار خارجه، ثم تقص كل خلية سمة اختبار إلى المجال المشاهد في التدريب وتقيس نسبة الخلايا المتغيرة؛ القياس وصفي ولا يثبت تأثيراً سببياً.

## الأسطر 53–61

```python
    for name in ["RandomForest", "GradientBoosting", "LSTM"]:
        predicted = models[name].predict(inputs[test])
        audit[name] = {"prediction_min": float(predicted.min()), "prediction_max": float(predicted.max()), "mean_price_error": float(np.mean(predicted - windows.y[test]))}
        if name != "LSTM":
            difference = float(np.max(np.abs(predicted - models[name].predict(clipped))))
            np.testing.assert_allclose(predicted, models[name].predict(clipped), atol=1e-9, rtol=1e-10)
            audit[name]["clip_to_training_feature_box_max_prediction_change"] = difference
    assert minimum - 1e-8 <= audit["RandomForest"]["prediction_min"] <= audit["RandomForest"]["prediction_max"] <= maximum + 1e-8
    return audit
```

تجمع مدى التنبؤ وانحيازه المتوسط للغابة والتعزيز وLSTM، وتختبر ثبات تنبؤ شجرتي الغابة والتعزيز عند قص السمات، وتؤكد وقوع توقعات الغابة ضمن مجال هدف التدريب. هذه assertions تخص الآثار المدققة ولا تبرهن تفوق نموذج.

## الأسطر 64–75

```python
def frozen_metric_check(folder, windows, models) -> list[dict]:
    table = pd.read_csv(folder / "predictions.csv")
    checked = []
    for name, group in table.groupby("model", sort=False):
        predicted = group.predicted.to_numpy()
        actual = group.actual.to_numpy()
        metrics = forecast_metrics(actual, predicted, group.current_close.to_numpy())
        if name in models:
            reloaded = models[name].predict(windows.flat[windows.partitions["test"]])
            np.testing.assert_allclose(reloaded, predicted, rtol=1e-5, atol=1e-4)
        checked.append({"model": name, **metrics})
    return checked
```

frozen_metric_check تقرأ تنبؤات CSV المحفوظة وتحسب المقاييس لكل نموذج وتفحص تنبؤ النموذج المعاد تحميله مقابل المحفوظ عند توفره؛ Persistence لا يعاد تحميله كنموذج. تعتمد ترتيب الصفوف المتطابق.

## الأسطر 78–92

```python
def audit_original(original, destination) -> None:
    audits, metrics = {}, []
    for asset in ["AAPL", "SP500", "NASDAQ", "GOLD", "OIL", "HOUSING"]:
        folder = original / asset
        windows = load_windows(folder)
        prices, manifest = load_snapshot(asset)
        rebuilt = build_windows(features(prices, manifest["frequency"]), windows.x.shape[1])
        np.testing.assert_array_equal(windows.x, rebuilt.x)
        np.testing.assert_array_equal(windows.y, rebuilt.y)
        models = load_models(folder, "cpu")
        audits[asset] = {"dataset": manifest, "alignment": alignment_check(windows, prices, manifest), "causality": causal_feature_check(prices, manifest["frequency"]), "scaling": scaler_check(windows, folder), "shift": distribution_shift(windows, models)}
        metrics.extend({"asset": asset, **row} for row in frozen_metric_check(folder, windows, models))
        print(f"AUDIT {asset}: alignment, causal features, training scalers and reload verified", flush=True)
    write_json(destination / "original_audit.json", audits)
    pd.DataFrame(metrics).to_csv(destination / "original_metrics_recalculated.csv", index=False)
```

audit_original تمر عبر ستة أصول، وتحمل اللقطة والنوافذ وتعيد بناء x وy وتتحقق من التطابق، وتحمل النماذج على CPU وتشغل فحوص المحاذاة والسمات والمعايير والانزياح والمقاييس ثم تكتب تقرير JSON وCSV. تشغيلها يعيد حساب تدقيقات ويتطلب آثاراً موثوقة؛ لم تنفذ في جلسة التوثيق.
