# شرح `src/xai_finance/explain/shap_explain.py`

بصمة المصدر SHA-256: `3bf26cc8a78f1c0b257e489739d5712edfa200af961aaebe10003bad5ded3e6b`.

الاقتباسات من المصدر؛ التفسير مراجعة يدوية لا إجراء حسابات جديدة.

## الأسطر 1–2

```python
import numpy as np
import shap
```

يستورد NumPy للمصفوفات وSHAP للمفسرات وكائن Explanation؛ مكتبتان خارجيتان.

## الأسطر 5–6

```python
def explain_shap(model_name: str, model, background: np.ndarray, request: dict) -> shap.Explanation:
    observations, names = request["observations"], request["names"]
```

explain_shap تقبل اسم النموذج وكائنه وbackground وطلباً يحوي observations وnames، وتعيد Explanation. يستدعيها مسار توليد التفسيرات؛ تفترض توافق الأشكال والأسماء.

## الأسطر 7–10

```python
    if model_name == "LinearRegression":
        scaler, selector, regressor = [step[1] for step in model.steps]
        explainer = shap.LinearExplainer(regressor, selector.transform(scaler.transform(background)))
        explanation = explainer(selector.transform(scaler.transform(observations)))
```

للخطي يفك الخطوات الثلاث scaler وselector وregressor من Pipeline، ويحول الخلفية والمشاهدات باستخدام المعاملات الملائمة ثم يستعمل LinearExplainer. تغيير ترتيب الخطوات يفشل هذا الافتراض.

## الأسطر 11–13

```python
        attributions = np.zeros_like(observations)
        attributions[:, selector.retained_] = explanation.values
        return shap.Explanation(values=attributions, base_values=explanation.base_values, data=observations, feature_names=names)
```

ينشئ مصفوفة أصفار كشكل المشاهدات ويضع قيم السمات المختارة في retained_ ثم يعيد Explanation بمرجع التفسير وبيانات وأسماء المجال الأصلي؛ الأصفار للسمات التي حذفها selector لا تثبت عدم أهميتها في نموذج بديل.

## الأسطر 14–18

```python
    if model_name in {"RandomForest", "GradientBoosting"}:
        explainer = shap.TreeExplainer(model, data=background, feature_perturbation="interventional")
        explanation = explainer(observations, check_additivity=True)
        explanation.feature_names = names
        return explanation
```

للغابة والتعزيز ينشئ TreeExplainer مع خلفية وfeature_perturbation="interventional"، ويفسر المشاهدات مع check_additivity ثم يضيف الأسماء ويعيد التفسير. آلية الإخفاء والخلفية تؤثران في الإسناد.

## الأسطر 19–21

```python
    masker = shap.maskers.Independent(background, max_samples=len(background))
    explainer = shap.PermutationExplainer(model.predict, masker, feature_names=names, seed=request["seed"])
    return explainer(observations, max_evals=request["cycles"] * (2 * observations.shape[1] + 1), batch_size=256, silent=True)
```

لأي اسم آخر ينشئ Independent masker من الخلفية وPermutationExplainer يستدعي model.predict ببذرة وأسماء؛ عدد تقييمات الطلب cycles×(2p+1) حيث p عدد الأعمدة، ودفعات 256. هذا تقريب يعتمد ميزانية التقييم وليس قيماً سببية.

## الأسطر 24–28

```python
def shap_reconstruction(explanation: shap.Explanation, predicted: np.ndarray) -> dict:
    reconstructed = np.asarray(explanation.base_values).reshape(-1) + explanation.values.sum(axis=1)
    errors = np.abs(reconstructed - predicted)
    np.testing.assert_allclose(reconstructed, predicted, rtol=1e-4, atol=1e-3)
    return {"max_absolute_error": float(errors.max()), "mean_absolute_error": float(errors.mean()), "rtol": 1e-4, "atol": 1e-3}
```

shap_reconstruction تجمع base_values ومساهمات الصف وتقارنها بتنبؤ النموذج ضمن rtol=1e-4 وatol=1e-3؛ تعيد أعظم ومتوسط فرق مطلق، وترفع AssertionError عند فشل allclose. الجمع لا يثبت أداء النموذج أو سلامة تفسير سببي.
