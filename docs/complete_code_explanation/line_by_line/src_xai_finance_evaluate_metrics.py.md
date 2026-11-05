# شرح `src/xai_finance/evaluate/metrics.py`

بصمة المصدر SHA-256: `2a89abe82731ef5e17cc351e0eaed243f08d66422ebe49985af9d2cbd00ff746`.

المقاطع مقتبسة من المصدر، والوصف مراجعة يدوية لا يشغل التجارب.

## الأسطر 1–2

```python
import numpy as np
from sklearn.metrics import confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
```

NumPy وsklearn مكتبتان خارجيتان للحساب العددي والمقاييس ومصفوفة الالتباس.

## الأسطر 5–10

```python
def forecast_metrics(actual: np.ndarray, predicted: np.ndarray, current: np.ndarray) -> dict:
    actual, predicted, current = [np.asarray(series, dtype=float).ravel() for series in (actual, predicted, current)]
    if len(actual) == 0 or actual.shape != predicted.shape or actual.shape != current.shape:
        raise ValueError("Aligned, nonempty actual/predicted/current arrays required")
    if not all(np.isfinite(series).all() for series in (actual, predicted, current)):
        raise ValueError("Metrics require finite values in original units")
```

forecast_metrics تستقبل actual وpredicted وcurrent وتسطحها كأعداد عشرية وتتحقق من تساوي الأشكال وغير الفراغ والقيم المنتهية؛ ترفع ValueError عند الإخلال. لا تتحقق بنفسها من الوحدات أو تواريخ المحاذاة.

## الأسطر 11–13

```python
    nonzero = np.abs(actual) > 1e-12
    up_true, up_pred = actual > current, predicted > current
    confusion = confusion_matrix(up_true, up_pred, labels=[False, True])
```

تحدد الأهداف غير القريبة من الصفر بـ |y|>1e-12، وتصنف الصعود بمقارنة القيمة مع current، وتبني مصفوفة ثنائية بترتيب False ثم True؛ التعادل يعامل كغير صعود فيها.

## الأسطر 14–14

```python
    return {"mae": float(mean_absolute_error(actual, predicted)), "rmse": float(np.sqrt(mean_squared_error(actual, predicted))), "mape_percent": float(np.mean(np.abs((actual[nonzero] - predicted[nonzero]) / actual[nonzero])) * 100) if nonzero.any() else None, "mape_excluded_zero_targets": int((~nonzero).sum()), "r2": float(r2_score(actual, predicted)) if len(actual) > 1 and np.ptp(actual) > 0 else None, "direction_accuracy": float(np.mean(np.sign(predicted - current) == np.sign(actual - current))), "up_down_confusion": confusion.tolist(), "up_precision": float(confusion[1, 1] / confusion[:, 1].sum()) if confusion[:, 1].sum() else None, "up_recall": float(confusion[1, 1] / confusion[1].sum()) if confusion[1].sum() else None, "n": len(actual)}
```

تعيد MAE=mean|y−ŷ| وRMSE=sqrt(mean(y−ŷ)²) وMAPE بالنسبة المئوية للغايات غير الصفرية وعدد المستبعد، وR² إذا تعددت القيم ولم يكن الهدف ثابتاً، ودقة إشارة التغير ثلاثية الحالات ومصفوفة الالتباس وprecision/recall للصعود والحجم. عند غياب مقام ملائم تعيد None. دقة الإشارة تميز التعادل بخلاف التصنيف الثنائي؛ MAPE قرب الصفر غير مستقر وR² المرتفع لمستوى السعر لا يثبت مهارة تداول.
