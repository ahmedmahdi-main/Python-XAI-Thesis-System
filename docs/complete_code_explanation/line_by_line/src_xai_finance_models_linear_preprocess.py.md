# شرح `src/xai_finance/models/linear_preprocess.py`

بصمة المصدر SHA-256: `9382546e4b3481cfe1eaa561614bb23772f02029e924f0b717d4b526600b35a2`.

المقاطع من المصدر الفعلي؛ لا تشغّل هذه الوثيقة التدريب أو تعدل الآثار. الأسطر الفارغة للتنسيق.

## الأسطر 1–3

```python
import numpy as np
from scipy.linalg import qr
from sklearn.base import BaseEstimator, TransformerMixin
```

NumPy للمصفوفات؛ qr من SciPy للتحليل QR؛ BaseEstimator وTransformerMixin من sklearn لتنفيذ محوّل متوافق مع Pipeline.

## الأسطر 6–10

```python
class IndependentColumns(TransformerMixin, BaseEstimator):
    """Training-only QR removes dependent coordinates before ordinary least squares."""

    def __init__(self, relative_tolerance: float = 1e-10):
        self.relative_tolerance = relative_tolerance
```

IndependentColumns محوّل يتعلم الأعمدة المستقلة عددياً من التدريب قبل OLS. يرث واجهة sklearn؛ relative_tolerance الافتراضي 1e-10 يحفظه المنشئ دون فحص خاص.

## الأسطر 12–15

```python
    def fit(self, inputs: np.ndarray, target=None):
        _, triangular, pivots = qr(inputs, mode="economic", pivoting=True)
        diagonal = np.abs(np.diag(triangular))
        self.rank_ = int((diagonal > diagonal[0] * self.relative_tolerance).sum())
```

fit تستقبل مصفوفة inputs وtarget اختياري غير مستخدم للتوافق مع sklearn. QR مع تبديل الأعمدة يعطي R ومؤشرات pivots؛ يتجاهل Q. يقدر الرتبة بعدد عناصر قطر R المطلقة التي تتجاوز أول عنصر مضروباً في التسامح. هذا تقدير عددي للرتبة وليس ضمان استقلال إحصائي.

## الأسطر 16–19

```python
        # A constant-only design still needs one column for sklearn's intercept-only OLS fit.
        self.retained_ = np.sort(pivots[:max(1, self.rank_)])
        self.n_features_in_ = inputs.shape[1]
        return self
```

حتى لو رتبة التقدير صفر يحتفظ بعمود واحد؛ يرتب فهارس الأعمدة المختارة ويخزن عدد السمات الأصلية ثم يعيد self طبقاً لبروتوكول fit. المصفوفة بلا أي عمود قد تفشل عند diagonal[0]؛ عدد الأعمدة المخزّن لا يفرض التحقق تلقائياً في transform.

## الأسطر 21–22

```python
    def transform(self, inputs: np.ndarray) -> np.ndarray:
        return np.asarray(inputs)[:, self.retained_]
```

transform تحول المدخل إلى مصفوفة وتعيد الأعمدة retained_ لجميع الصفوف. تستدعى بعد fit بواسطة Pipeline؛ لا تعيد ملاءمة الاختيار على بيانات التحقق أو الاختبار. فهرسة مدخل قبل fit أو بشكل غير متوافق قد تفشل.
