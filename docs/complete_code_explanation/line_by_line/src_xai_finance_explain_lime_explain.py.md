# شرح `src/xai_finance/explain/lime_explain.py`

بصمة المصدر SHA-256: `3ec646ba008e1fc255ebc9b8bb0eeaecefb9be679f3df4471c2ef658692f5bc3`.

الاقتباسات من المصدر؛ التفسير مراجعة يدوية لا إجراء حسابات جديدة.

## الأسطر 1–2

```python
import numpy as np
from lime.lime_tabular import LimeTabularExplainer
```

يستورد NumPy لتلميحات الأنواع وLimeTabularExplainer من مكتبة LIME الخارجية.

## الأسطر 5–7

```python
def explain_lime(training: np.ndarray, predict, observation: np.ndarray, request: dict):
    explainer = LimeTabularExplainer(training, feature_names=request["names"], mode="regression", discretize_continuous=True, random_state=request["seed"], feature_selection="highest_weights")
    explanation = explainer.explain_instance(observation, predict, num_features=10, num_samples=request["samples"])
```

explain_lime تستقبل بيانات تدريب ودالة predict وعينة وقاموس إعداد؛ تنشئ مفسر انحدار بأسماء السمات وتقطيع مستمر وبذرة واختيار أعلى الأوزان. تطلب تفسير العينة باستخدام عشر سمات وعدد perturbations من samples. يعاد استخدام بيانات التدريب كمرجع لتوليد الجوار لا كدليل سببي.

## الأسطر 8–11

```python
    local_prediction = float(explanation.local_pred[0])
    prediction = float(predict(observation[None])[0])
    audit = {"model_prediction": prediction, "local_surrogate_prediction": local_prediction, "absolute_local_error": abs(prediction - local_prediction), "weighted_neighborhood_r2": float(explanation.score), "seed": request["seed"], "num_samples": request["samples"], "features": explanation.as_list()}
    return explanation, audit
```

تستخرج التنبؤ المحلي من البديل وتنبؤ النموذج على العينة ذات محور دفعة، وتبني قاموس الفرق المطلق وقيمة `explanation.score` المخزنة باسم `weighted_neighborhood_r2` والبذرة وعدد العينات والأوزان، ثم تعيد كائن التفسير والتدقيق. في نسخة LIME المحلية المفحوصة تمثل الدرجة R² موزونة على الجوار؛ يتطابق رقم إصدارها مع سجل التجربة، لكن هوية تثبيتها التاريخي لم تثبت بالبصمة. قد يكون تقريب الجوار ضعيفاً خصوصاً في أبعاد مترابطة. راجع [تدقيق المنشأ](../LIME_PROVENANCE_REVIEW_AR.md).
