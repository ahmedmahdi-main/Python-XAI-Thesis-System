# شرح `tests/test_provider_integration.py`

بصمة المصدر SHA-256: `b53ad6c2aa4b7d61ed4a0280cad3b641e7e797970c3ad5eea9bb5573a9b7548c`.

وصف الاختبارات لا يعني أنها شُغلت في جلسة التوثيق.

## الأسطر 1–8

```python
import numpy as np
import pytest

from xai_finance.data.features import features
from xai_finance.data.windows import build_windows
from xai_finance.explain.shap_explain import explain_shap, shap_reconstruction
from xai_finance.io.data_sources import load_snapshot
from xai_finance.models.sklearn_models import candidates, fit_candidates
```

يستورد أدوات بناء البيانات والنماذج وSHAP وتحميل اللقطة للتحقق التكاملي.

## الأسطر 11–22

```python
@pytest.mark.integration
def test_real_provider_ols_explanation_reconstructs_stably():
    """Regression: provider-rounded dependent features caused catastrophic OLS cancellation."""
    prices, _ = load_snapshot("AAPL")
    windows = build_windows(features(prices, "daily"), 30)
    model, _ = fit_candidates(candidates({"seed": 42, "trees": 5, "search": False})["LinearRegression"], windows)
    indices = windows.partitions["test"][np.linspace(0, len(windows.partitions["test"]) - 1, 10, dtype=int)]
    background = windows.flat[windows.partitions["train"][np.linspace(0, len(windows.partitions["train"]) - 1, 8, dtype=int)]]
    request = {"observations": windows.flat[indices], "names": windows.flat_names, "seed": 42, "cycles": 1}
    explanation = explain_shap("LinearRegression", model, background, request)
    audit = shap_reconstruction(explanation, model.predict(windows.flat[indices]))
    assert audit["max_absolute_error"] < 1e-3
```

اختبار integration يحمل لقطة AAPL المحلية، ويبني النوافذ ويلائم OLS على التدريب، ويختار 10 اختبارات و8 خلفيات ويفحص إعادة بناء SHAP بأقل من 1e-3. يتطلب لقطة محفوظة ويدرّب نموذج اختبار؛ لا يثبت إعادة إنتاج الرسالة.
