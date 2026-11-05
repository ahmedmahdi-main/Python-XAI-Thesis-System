# شرح `src/xai_finance/models/sklearn_models.py`

بصمة المصدر SHA-256: `8c362c55823c423b21172dbc532f21155f3d3715895f191b55a601704b2eade7`.

المقاطع من المصدر الفعلي؛ لا تشغّل هذه الوثيقة التدريب أو تعدل الآثار. الأسطر الفارغة للتنسيق.

## الأسطر 1–11

```python
from time import perf_counter

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from xai_finance.data.windows import WindowDataset
from xai_finance.models.linear_preprocess import IndependentColumns
```

perf_counter مؤقت معياري؛ NumPy للحسابات؛ sklearn توفر نموذجي الأشجار وLinearRegression وMSE وPipeline وStandardScaler. WindowDataset وIndependentColumns وحدتان داخليتان.

## الأسطر 14–17

```python
def candidates(configuration: dict) -> dict[str, list]:
    seed, trees = configuration["seed"], configuration["trees"]
    forests = [RandomForestRegressor(n_estimators=trees, max_depth=5, min_samples_leaf=3, random_state=seed, n_jobs=4)]
    boosters = [GradientBoostingRegressor(n_estimators=trees, max_depth=2, learning_rate=0.03, random_state=seed)]
```

candidates تستقبل configuration وتقرأ seed وtrees؛ تنشئ مرشح غابة بعمق 5 وأقل ورقة 3 وبأربعة عمال، ومرشح تعزيز بعمق 2 ومعدل تعلم 0.03. عدد الأشجار والبذرة من الإعداد لا ثوابت عامة.

## الأسطر 18–21

```python
    if configuration["search"]:
        forests.append(RandomForestRegressor(n_estimators=trees, max_depth=10, min_samples_leaf=3, random_state=seed, n_jobs=4))
        boosters.append(GradientBoostingRegressor(n_estimators=trees, max_depth=3, learning_rate=0.1, random_state=seed))
    return {"LinearRegression": [make_pipeline(StandardScaler(), IndependentColumns(), LinearRegression())], "RandomForest": forests, "GradientBoosting": boosters}
```

عند search تضيف غابة عمق 10 وتعزيزاً بعمق 3 ومعدل 0.1، ثم تعيد قاموس قوائم المرشحين. الانحدار يتكون من StandardScaler ثم IndependentColumns ثم LinearRegression؛ ملاءمة Pipeline تطبق الخطوتين على التدريب فقط.

## الأسطر 24–29

```python
def fit_candidates(estimators: list, windows: WindowDataset) -> tuple[object, dict]:
    training, validation = windows.partitions["train"], windows.partitions["validation"]
    trials = []
    fitted = []
    for estimator in estimators:
        started = perf_counter()
```

fit_candidates تأخذ قائمة المقدرات والنوافذ وتستخرج فهارس التدريب والتحقق وتنشئ سجلات ومرشحين ملائمين؛ لكل مرشح تبدأ ساعة القياس. لا يقرأ الاختبار في هذه الدالة.

## الأسطر 30–33

```python
        estimator.fit(windows.flat[training], windows.y[training])
        rmse = float(np.sqrt(mean_squared_error(windows.y[validation], estimator.predict(windows.flat[validation]))))
        trials.append({"parameters": str(estimator), "validation_rmse": rmse, "elapsed_seconds": perf_counter() - started})
        fitted.append(estimator)
```

يلائم المرشح على النوافذ المسطحة وأهداف التدريب ثم يحسب جذر متوسط مربع خطأ التحقق ويسجل المعاملات والزمن ويحتفظ بالكائن المُلائم. التحقق يُستخدم للاختيار وليس تقديراً نهائياً غير متحيز للأداء.

## الأسطر 34–38

```python
    selected = int(np.argmin([trial["validation_rmse"] for trial in trials]))
    selected_model = fitted[selected]
    if isinstance(selected_model, RandomForestRegressor):
        selected_model.set_params(n_jobs=1)
    return selected_model, {"selection": "validation RMSE only; no test access; no refit", "selected_trial": selected, "trials": trials, "training_seconds": sum(trial["elapsed_seconds"] for trial in trials), "inference": "Forest predictions sum trees serially for deterministic floating-point accumulation"}
```

argmin يختار أدنى RMSE ويعيد النموذج المُلائم بلا إعادة تدريب مع قاموس التفاصيل؛ للغابة يضبط n_jobs=1 لتجميع أشجار متسلسل في الاستدلال. trials فارغة تؤدي إلى فشل argmin؛ يضمن المسار المعتاد وجود مرشحين.
