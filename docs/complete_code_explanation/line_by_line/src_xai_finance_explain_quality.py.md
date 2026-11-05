# شرح `src/xai_finance/explain/quality.py`

بصمة المصدر SHA-256: `e1f89e524a7473a6dfbc2a05c0cf41cf94302e77201d3c0f98a949b5b3349072`.

الاقتباسات من المصدر؛ التفسير مراجعة يدوية لا إجراء حسابات جديدة.

## الأسطر 1–2

```python
import numpy as np
from scipy.stats import spearmanr
```

NumPy للحسابات وspearmanr من SciPy لارتباط الرتب؛ مكتبتان خارجيتان.

## الأسطر 5–8

```python
def attribution_stability(first: np.ndarray, second: np.ndarray) -> dict:
    first, second = np.abs(first), np.abs(second)
    count = min(10, len(first))
    overlap = len(set(np.argsort(first)[-count:]) & set(np.argsort(second)[-count:])) / count
```

attribution_stability تستقبل متجهي إسهام وتقارن قيمهما المطلقة؛ تختار أصغر 10 وعدد السمات وتحسب نسبة تداخل فهارس أعلى الإسهامات. تساوي 1 يدل على تطابق المجموعتين وفق ترتيب argsort، لا على تطابق القيم.

## الأسطر 9–10

```python
    correlation = spearmanr(first, second).statistic if np.ptp(first) and np.ptp(second) else None
    return {"top_10_overlap": overlap, "spearman_abs_attribution_rank": float(correlation) if correlation is not None and np.isfinite(correlation) else None, "scope": "Same observation rerun with a different explainer seed; not human trust or robustness to all market shifts"}
```

تحسب ارتباط Spearman للرتب المطلقة عند تغير كلا المتجهين، وتعطي None للقيمة غير المتاحة أو غير المنتهية؛ تعيد أيضاً توصيف نطاق اختبار بذرتين للعينة نفسها. المتجه الفارغ قد يسبب قسمة على صفر، وتفترض الدالة تطابق أطوال الإدخال.

## الأسطر 13–17

```python
def lime_weight_vector(explanation, count: int) -> np.ndarray:
    weights = np.zeros(count)
    for feature, weight in explanation.as_map()[1]:
        weights[feature] = weight
    return weights
```

lime_weight_vector تنشئ متجه أصفار بطول count وتملؤه بأوزان feature من explanation.as_map()[1]، ثم تعيده. السمات غير الظاهرة تبقى صفراً؛ هذا لا يثبت انعدام أهميتها خارج البديل المحدود. تفترض وجود المفتاح 1 وفهارس ضمن المجال.
