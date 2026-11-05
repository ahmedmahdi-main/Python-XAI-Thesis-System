# شرح `src/xai_finance/data/preprocess.py`

بصمة المصدر SHA-256: `795123aca48a8ee72b305571c46707aa19428e248927ddc162a2a28ca46ff2b0`.

الاقتباسات من المصدر الفعلي؛ الأسطر الفارغة للتنسيق. لا ينفذ هذا الشرح التدريب أو يعدل البيانات.

## الأسطر 1–6

```python
from dataclasses import dataclass

import numpy as np
from sklearn.preprocessing import StandardScaler

from xai_finance.data.windows import WindowDataset
```

dataclass من المكتبة القياسية، وNumPy وStandardScaler من مكتبتين خارجيتين، وWindowDataset نوع داخلي.

## الأسطر 9–14

```python
@dataclass
class TrainingScalers:
    inputs: StandardScaler
    target: StandardScaler
    fitted_origin_cutoff: str
    fitted_target_cutoff: str
```

TrainingScalers حاوية لمعياري المدخلات والهدف ونص تاريخ آخر أصل وآخر هدف استُعمل في الملاءمة. ينشئ dataclass منشئاً وفق ترتيب الحقول.

## الأسطر 16–18

```python
    def transform_windows(self, windows: np.ndarray) -> np.ndarray:
        shape = windows.shape
        return self.inputs.transform(windows.reshape(-1, shape[-1])).reshape(shape).astype(np.float32)
```

transform_windows تحفظ الشكل، وتسطح كل الخطوات إلى صفوف سمات، وتطبق معيار المدخلات المُلائم، ثم تعيد الشكل الأصلي وتحول إلى float32؛ لا تعيد ملاءمة المعيار.

## الأسطر 20–21

```python
    def inverse_target(self, predictions: np.ndarray) -> np.ndarray:
        return self.target.inverse_transform(np.asarray(predictions).reshape(-1, 1)).ravel()
```

inverse_target تحول التنبؤات إلى عمود، وتطبق inverse_transform لمعيار الهدف، ثم ravel لإرجاع متجه بالوحدات الأصلية. الصيغة x=zσ+μ وفق معلمات التدريب.

## الأسطر 24–28

```python
def fit_training_scalers(windows: WindowDataset) -> TrainingScalers:
    training = windows.partitions["train"]
    sequence = windows.x[training]
    scalers = TrainingScalers(StandardScaler().fit(sequence.reshape(-1, sequence.shape[-1])), StandardScaler().fit(windows.y[training, None]), str(windows.origins[training[-1]].date()), str(windows.targets[training[-1]].date()))
    return scalers
```

fit_training_scalers تختار فهارس التدريب والنوافذ الموافقة، وتلائم StandardScaler للمدخلات على جميع خطوات نوافذ التدريب وللهدف على أهداف التدريب فقط، وتوثق آخر تواريخ الأصل والهدف وتعيد الحاوية. النوافذ المتداخلة تكرر بعض الرصود في ملاءمة المدخلات؛ لا تستعمل أهداف الاختبار. يستدعيها fit_lstm.
