# شرح `src/xai_finance/evaluate/regimes.py`

بصمة المصدر SHA-256: `13f423ee03fd1f069ce5ce5129216e6fa6649873cf6bd48e0f16faceb305f152`.

المقاطع مقتبسة من المصدر، والوصف مراجعة يدوية لا يشغل التجارب.

## الأسطر 1–4

```python
import numpy as np
import pandas as pd

from xai_finance.evaluate.metrics import forecast_metrics
```

NumPy للتصنيف وpandas للجدول من مكتبات خارجية، وforecast_metrics دالة داخلية.

## الأسطر 7–8

```python
def regime_labels(trailing_returns: np.ndarray, threshold: float) -> np.ndarray:
    return np.select([trailing_returns > threshold, trailing_returns < -threshold], ["bull", "bear"], default="sideways")
```

regime_labels تقبل عوائد متأخرة وعتبة، وتعيد bull إذا زاد العائد عن threshold وbear إن قل عن سالبها وإلا sideways؛ المساواة تدخل sideways. لا تتحقق من إيجابية العتبة أو انتهاء القيم.

## الأسطر 11–15

```python
def regime_metrics(predictions: pd.DataFrame) -> list[dict]:
    summaries = []
    for (model, regime), subset in predictions.groupby(["model", "regime"]):
        summaries.append({"model": model, "regime": regime, **forecast_metrics(subset.actual, subset.predicted, subset.current_close)})
    return summaries
```

regime_metrics تقسم DataFrame حسب model وregime وتستدعي forecast_metrics لكل مجموعة وتعيد قائمة قواميس؛ لا تولد فئات غائبة. المجموعات الصغيرة وصفية وقد تكون تقديراتها غير مستقرة.
