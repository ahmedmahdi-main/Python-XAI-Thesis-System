# شرح `src/xai_finance/validation/statistics.py`

بصمة المصدر SHA-256: `973bcca38ac776ed48d48ede9b73fb194f045600fe0eec80971a96b2253d9ac3`.

المقاطع مقتبسة من المصدر، والوصف مراجعة يدوية لا يشغل التجارب.

## الأسطر 1–3

```python
import numpy as np

from xai_finance.evaluate.metrics import forecast_metrics
```

NumPy خارجية وforecast_metrics داخلية لإعادة استعمال مقاييس السعر.

## الأسطر 6–10

```python
def directional_statistics(actual_change: np.ndarray, predicted_change: np.ndarray) -> dict:
    actual_sign, predicted_sign = np.sign(actual_change), np.sign(predicted_change)
    active = predicted_sign != 0
    hits = actual_sign == predicted_sign
    return {"direction_accuracy": float(np.mean(hits)), "direction_coverage": float(np.mean(active)), "direction_accuracy_when_active": float(np.mean(hits[active])) if active.any() else None, "binary_up_accuracy_zero_is_not_up": float(np.mean((actual_change > 0) == (predicted_change > 0))), "actual_up_fraction": float(np.mean(actual_change > 0)), "actual_flat_fraction": float(np.mean(actual_change == 0))}
```

directional_statistics تقارن sign للتغير الفعلي والمتوقع بثلاث حالات، وتحسب نسبة التنبؤ غير الصفري ودقته المشروطة ودقة الصعود الثنائية مع الصفر غير صعود ونسب الصعود والثبات. إذا لم توجد تنبؤات نشطة ترجع None للدقة المشروطة؛ الامتناع لا يساوي بالضرورة قرار هبوط.

## الأسطر 13–20

```python
def paired_bootstrap(actual: np.ndarray, predicted: np.ndarray, zero: np.ndarray) -> dict:
    loss_difference = (predicted - actual) ** 2 - (zero - actual) ** 2
    generator = np.random.default_rng(42)
    block_length, draws = 10, 2000
    starts = generator.integers(0, len(actual), size=(draws, int(np.ceil(len(actual) / block_length))))
    indices = ((starts[..., None] + np.arange(block_length)) % len(actual)).reshape(draws, -1)[:, :len(actual)]
    interval = np.quantile(loss_difference[indices].mean(axis=1), [0.025, 0.975])
    return {"mse_difference_vs_zero": float(np.mean(loss_difference)), "mse_difference_ci_low": float(interval[0]), "mse_difference_ci_high": float(interval[1]), "bootstrap_block_length": block_length, "bootstrap_draws": draws, "bootstrap_seed": 42}
```

paired_bootstrap تحسب dₜ=(ŷₜ−yₜ)²−(zeroₜ−yₜ)² على المشاهدات المزدوجة؛ السالب لصالح النموذج. بمولد seed=42 تختار بدايات 2000 إعادة أخذ كتل دائرية طولها 10 وتلتف modulo n، وتحسب متوسط d لكل عينة وكمّي 2.5% و97.5%. الفرق بوحدة السعر المربعة لا RMSE. الفاصل تقريبي لاستقرار الاعتماد الزمني ولا يشمل عدم يقين إعادة التدريب أو تصحيح تعدد المقارنات؛ الإدخال الفارغ غير صالح.

## الأسطر 23–31

```python
def evaluation_metrics(table) -> dict:
    actual, predicted, current = [table[column].to_numpy() for column in ["actual_price", "predicted_price", "current_price"]]
    metrics = forecast_metrics(actual, predicted, current)
    metrics.update(directional_statistics(actual - current, predicted - current))
    metrics.update(paired_bootstrap(actual, predicted, current))
    metrics["rmse_ratio_vs_zero"] = metrics["rmse"] / float(np.sqrt(np.mean((actual - current) ** 2)))
    target_metrics = forecast_metrics(table.actual_target.to_numpy(), table.predicted_target.to_numpy(), np.zeros(len(table)))
    metrics.update({f"target_{name}": target_metrics[name] for name in ["mae", "rmse", "r2", "mape_percent", "mape_excluded_zero_targets"]})
    return metrics
```

evaluation_metrics تستخرج السعر الحقيقي والمتوقع والحالي، تجمع مقاييس السعر والإشارة وbootstrap مقابل الثبات، ثم نسبة RMSE إلى RMSE الثبات ومقاييس الهدف المحول مقابل صفر. عند مقام ثبات صفري قد تكون النسبة غير معرفة؛ MAPE للأهداف الصغيرة غير مستقر ولا يمثل معيار اختيار هنا.
