# شرح `src/xai_finance/data/windows.py`

بصمة المصدر SHA-256: `5a2dd67bb06590ee870e77dff8787faeb89027f2de566095b50b6295d5728743`.

الاقتباسات من المصدر الفعلي؛ الأسطر الفارغة للتنسيق. لا ينفذ هذا الشرح التدريب أو يعدل البيانات.

## الأسطر 1–6

```python
from dataclasses import dataclass

import numpy as np
import pandas as pd

from xai_finance.data.split import chronological_indices
```

dataclass من المكتبة القياسية لإنشاء حاوية البيانات؛ NumPy وpandas خارجيتان. chronological_indices استيراد داخلي لتقسيم الفهارس زمنياً.

## الأسطر 9–18

```python
@dataclass
class WindowDataset:
    x: np.ndarray
    y: np.ndarray
    origins: pd.DatetimeIndex
    targets: pd.DatetimeIndex
    current_close: np.ndarray
    trailing_returns: np.ndarray
    feature_names: list[str]
    partitions: dict[str, np.ndarray]
```

WindowDataset صنف بيانات يولد dataclass منشئه؛ x نوافذ ثلاثية الأبعاد، y أهداف، origins تواريخ آخر مدخل، targets تواريخ الأهداف، current_close وtrailing_returns للقيم عند الأصل، وأسماء السمات وقواميس التقسيم. التلميحات لا تتحقق من الأشكال وحدها.

## الأسطر 20–22

```python
    @property
    def flat(self) -> np.ndarray:
        return self.x.reshape(len(self.x), -1)
```

خاصية flat تعيد تشكيل x إلى صف لكل نافذة وعمود لكل زوج زمن/سمة؛ -1 يستنتج عدد الأعمدة. تستعملها النماذج الجدولية بينما تحتفظ x ببعد الزمن لـ LSTM.

## الأسطر 24–26

```python
    @property
    def flat_names(self) -> list[str]:
        return [f"lag_{lag}__{name}" for lag in range(self.x.shape[1] - 1, -1, -1) for name in self.feature_names]
```

خاصية flat_names تبني أسماء lag تنازلياً من lookback−1 إلى 0، ثم السمات حسب ترتيبها لكل تأخر؛ توافق ترتيب التسطيح طالما ترتيب أبعاد x المعتاد لم يتغير.

## الأسطر 29–31

```python
def build_windows(engineered: pd.DataFrame, lookback: int) -> WindowDataset:
    if lookback < 1:
        raise ValueError("lookback must be positive")
```

build_windows تستقبل جدول سمات مرتباً زمنياً وطول نافذة، وترفع ValueError إن كان lookback أقل من واحد. لا تفحص ترتيب فهرس التاريخ هنا.

## الأسطر 32–34

```python
    # Boundary cases: first origin has exactly lookback rows; final row is context only.
    origins = np.arange(lookback - 1, len(engineered) - 1)
    partitions = chronological_indices(len(origins))
```

التعليق يشرح الحد؛ origins من lookback−1 حتى ما قبل آخر صف، وتستدعي chronological_indices لتقسيم عدد الأصول. آخر صف لا يمكن أن يكون أصلاً له هدف تالٍ، لكنه يصلح هدفاً للأصل السابق؛ عبارة التعليق final row is context only مضللة إذا فُهمت على أنها تنفي ذلك.

## الأسطر 35–36

```python
    matrix = engineered.to_numpy(dtype=np.float64)
    windows = np.stack([matrix[position - lookback + 1:position + 1] for position in origins])
```

يحوّل الجدول لمصفوفة float64 ويبني لكل أصل شريحة تضم lookback صفوفاً حتى الأصل شاملاً ثم يكدسها. عند عدم كفاية العينات يرفض التقسيم الأقل من 30 قبل الوصول إلى stack.

## السطر 37

```python
    return WindowDataset(windows, engineered.close.iloc[origins + 1].to_numpy(), engineered.index[origins], engineered.index[origins + 1], engineered.close.iloc[origins].to_numpy(), engineered.trailing_return_20.iloc[origins].to_numpy(), list(engineered.columns), partitions)
```

يعيد WindowDataset بالترتيب: النوافذ، إغلاق الصف التالي هدفاً، تاريخ الأصل والهدف، الإغلاق والعائد المتأخر عند الأصل، أسماء الأعمدة، والتقسيمات. يعتمد الوصول إلى close وtrailing_return_20 على وجودهما؛ لا يقرأ ملفات أو يكتبها.
