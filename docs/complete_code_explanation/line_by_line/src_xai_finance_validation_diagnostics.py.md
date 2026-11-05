# شرح `src/xai_finance/validation/diagnostics.py`

بصمة المصدر SHA-256: `8f047fe994c63b1dc661ca8f5a885b6076a0fbfce9142833527d41d7b4e575a9`.

المقاطع من المصدر؛ التفسير مراجعة يدوية دون تشغيل التجارب.

## الأسطر 1–8

```python
import joblib
import numpy as np
import pandas as pd
import torch

from xai_finance.pipelines.train import load_windows
from xai_finance.storage import read_json, write_json
from xai_finance.validation.statistics import directional_statistics, paired_bootstrap
```

joblib وNumPy وpandas وtorch خارجية؛ تحميل النوافذ والتخزين ومقاييس الاتجاه وbootstrap من المشروع.

## الأسطر 11–19

```python
def target_distribution(windows) -> list[dict]:
    rows = []
    for partition, indices in windows.partitions.items():
        series = {"price": windows.y[indices], "price_change": windows.y[indices] - windows.current_close[indices]}
        if np.all(windows.current_close > 0) and np.all(windows.y > 0):
            series["simple_return"] = windows.y[indices] / windows.current_close[indices] - 1
        for target, observations in series.items():
            rows.append({"partition": partition, "target": target, "mean": float(np.mean(observations)), "std": float(np.std(observations)), "min": float(np.min(observations)), "max": float(np.max(observations)), "n": len(observations)})
    return rows
```

target_distribution تصف لكل قسم السعر والتغير، وتضيف العائد فقط إذا كانت جميع الأسعار الحالية والأهداف في windows موجبة؛ ترجع المتوسط والانحراف الافتراضي ddof=0 والحدين والعدد. الشرط عام للبيانات كلها لا القسم وحده.

## الأسطر 22–29

```python
def lstm_output_bound(folder) -> dict:
    checkpoint = torch.load(folder / "LSTM/best.pt", map_location="cpu", weights_only=True)
    weight = checkpoint["state_dict"]["output.weight"].numpy()
    bias = float(checkpoint["state_dict"]["output.bias"].item())
    radius = float(np.abs(weight).sum())
    scalers = joblib.load(folder / "LSTM/scalers.joblib")
    bounds = scalers.inverse_target(np.array([bias - radius, bias + radius]))
    return {"price_lower_bound": float(bounds[0]), "price_upper_bound": float(bounds[1]), "derivation": "At inference dropout is disabled; each LSTM hidden coordinate is o*tanh(c) in [-1,1]; affine head is within bias +/- L1 norm of weights; then inverse training-target scaler. Bounds need not be attainable jointly."}
```

lstm_output_bound تحمل checkpoint CPU ومعيار الهدف؛ تحسب مجموع القيم المطلقة لأوزان الرأس r=Σ|wᵢ| وتستنتج المجال المعياري [b−r,b+r] لأن كل hᵢ ضمن [−1,1] أثناء الاستدلال، ثم تعكس معيار الهدف. الحدود محافظة وقد لا تتحقق جميع إحداثياتها معاً، ولا تعمم على بنية مختلفة.

## الأسطر 32–43

```python
def supplemental_audit(original, destination) -> None:
    distributions, original_comparisons, bounds = [], [], {}
    for asset in ["AAPL", "SP500", "NASDAQ", "GOLD", "OIL", "HOUSING"]:
        folder = original / asset
        windows = load_windows(folder)
        distributions.extend({"asset": asset, **row} for row in target_distribution(windows))
        bounds[asset] = lstm_output_bound(folder)
        table = pd.read_csv(folder / "predictions.csv")
        stored = {row["model"]: row for row in read_json(folder / "metrics.json")}
        test, train = windows.partitions["test"], windows.partitions["train"]
        outside_distance = np.maximum(windows.y[train].min() - windows.y[test], 0) + np.maximum(windows.y[test] - windows.y[train].max(), 0)
        bounds[asset]["random_forest_unavoidable_rmse_from_training_target_bounds"] = float(np.sqrt(np.mean(outside_distance ** 2)))
```

supplemental_audit تقرأ ستة أصول ونوافذها وتستخرج توزيعات وحدود LSTM والمقاييس المحفوظة، وتحسب المسافة خارج مجال هدف التدريب وجذر متوسط مربعاتها كحد أدنى لخطأ غابة مخرجاتها داخل ذلك المجال.

## الأسطر 44–51

```python
        for name, group in table.groupby("model", sort=False):
            actual, predicted, current = [group[column].to_numpy() for column in ["actual", "predicted", "current_close"]]
            rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))
            np.testing.assert_allclose(rmse, stored[name]["rmse"], rtol=1e-12)
            original_comparisons.append({"asset": asset, "model": name, "rmse": rmse, **directional_statistics(actual - current, predicted - current), **paired_bootstrap(actual, predicted, current)})
    pd.DataFrame(distributions).to_csv(destination / "target_distributions.csv", index=False)
    pd.DataFrame(original_comparisons).to_csv(destination / "original_comparisons.csv", index=False)
    write_json(destination / "architecture_bounds.json", bounds)
```

تقارن RMSE المعاد حسابه لكل نموذج بالقيمة المحفوظة وتضيف إحصاءات الاتجاه وbootstrap، ثم تحفظ جداول التوزيع والمقارنة وحدود البنية. لم تنفذ الحسابات في هذا العمل.

## الأسطر 54–60

```python
def prediction_amplitudes(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in predictions.groupby(["design", "target", "asset", "model"]):
        actual, predicted = group.actual_target.to_numpy(), group.predicted_target.to_numpy()
        actual_std, predicted_std = float(np.std(actual)), float(np.std(predicted))
        rows.append({**dict(zip(["design", "target", "asset", "model"], keys)), "observed_target_std": actual_std, "predicted_target_std": predicted_std, "predicted_to_observed_std": predicted_std / actual_std, "observed_target_mean": float(np.mean(actual)), "predicted_target_mean": float(np.mean(predicted)), "target_correlation": float(np.corrcoef(actual, predicted)[0, 1]) if predicted_std > 1e-12 else None})
    return pd.DataFrame(rows)
```

prediction_amplitudes تجمع بحسب التصميم والهدف والأصل والنموذج وتصف انحراف ومتوسط الهدف الحقيقي والمتوقع ونسبتهما وارتباطهما إن كان انحراف المتوقع كافياً. إذا كان انحراف الفعلي صفراً فقد تكون النسبة أو الارتباط غير صالحين؛ انخفاض التباين ليس برهان مهارة.
