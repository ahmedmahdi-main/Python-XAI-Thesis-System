# شرح `tests/test_explain_consistency.py`

بصمة المصدر SHA-256: `1f5cfcbbdfcc19a8085cf5345073b26973612b89c41d0b379bff0cac53d48065`.

وصف الاختبارات لا يعني أنها شُغلت في جلسة التوثيق.

## الأسطر 1–6

```python
import numpy as np
import pytest

from xai_finance.explain.lime_explain import explain_lime
from xai_finance.explain.shap_explain import explain_shap, shap_reconstruction
from xai_finance.models.sklearn_models import candidates, fit_candidates
```

يستورد أدوات NumPy وpytest ودوال التفسير وملاءمة النماذج.

## الأسطر 9–19

```python
@pytest.mark.parametrize("model_name", ["LinearRegression", "RandomForest", "GradientBoosting"])
def test_shap_additivity_and_posthoc_explanation_preserve_forecast(window_fixture, model_name):
    model, _ = fit_candidates(candidates({"seed": 42, "trees": 5, "search": False})[model_name], window_fixture)
    observations = window_fixture.flat[window_fixture.partitions["test"][:2]]
    before = model.predict(observations)
    background = window_fixture.flat[window_fixture.partitions["train"][::50]]
    request = {"observations": observations, "names": window_fixture.flat_names, "seed": 42, "cycles": 1}
    explanation = explain_shap(model_name, model, background, request)
    audit = shap_reconstruction(explanation, before)
    np.testing.assert_array_equal(before, model.predict(observations))
    assert audit["max_absolute_error"] < 0.01
```

اختبار معلم لثلاثة نماذج جدولية: يلائم نموذجاً صغيراً على fixture ويحسب تفسير SHAP لعينتين بخلفية تدريبية، ثم يتحقق من الجمع وثبات التوقع وخطأ إعادة البناء أقل من 0.01؛ لا يثبت سببية التفسير.

## الأسطر 22–30

```python
def test_lime_accepts_batch_prediction_and_returns_measured_surrogate_error(window_fixture):
    model, _ = fit_candidates(candidates({"seed": 42, "trees": 5, "search": False})["GradientBoosting"], window_fixture)
    training = window_fixture.flat[window_fixture.partitions["train"]]
    observation = window_fixture.flat[window_fixture.partitions["test"][0]]
    before = model.predict(observation[None])
    _, audit = explain_lime(training, model.predict, observation, {"names": window_fixture.flat_names, "seed": 42, "samples": 100})
    np.testing.assert_array_equal(before, model.predict(observation[None]))
    assert audit["absolute_local_error"] == pytest.approx(abs(audit["model_prediction"] - audit["local_surrogate_prediction"]))
    assert np.isfinite(audit["weighted_neighborhood_r2"])
```

يلائم GradientBoosting صغيراً ويشرح عينة بـ100 اضطراب، ويتحقق من عدم تغيير التنبؤ ومن أن الخطأ هو القيمة المطلقة للفرق بين النموذج والبديل وأن R² الجوار منتهٍ؛ لا يشترط جودة البديل.
