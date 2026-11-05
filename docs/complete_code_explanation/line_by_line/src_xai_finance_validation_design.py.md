# شرح `src/xai_finance/validation/design.py`

بصمة المصدر SHA-256: `83b2b73a3bb421842adf2296cf89272dc25883daa8fb03aa24e95bdeed72c9fc`.

المقاطع مقتبسة من المصدر، والوصف مراجعة يدوية لا يشغل التجارب.

## الأسطر 1–5

```python
from dataclasses import replace

import numpy as np

from xai_finance.data.windows import WindowDataset
```

replace القياسية تنسخ dataclass مع تغيير حقل، وNumPy خارجية، وWindowDataset نوع المشروع.

## الأسطر 8–15

```python
def target_values(windows: WindowDataset, target: str) -> np.ndarray:
    if target == "price_change":
        return windows.y - windows.current_close
    if target == "simple_return":
        if np.any(windows.current_close <= 0) or np.any(windows.y <= 0):
            raise ValueError("Simple-return protocol requires strictly positive prices")
        return windows.y / windows.current_close - 1
    raise ValueError(f"Unknown target: {target}")
```

target_values تحول الهدف إلى فرق السعر y−current أو عائد y/current−1؛ العائد يتطلب أن تكون جميع الأسعار الحالية والمستقبلية موجبة وإلا ValueError، والأسماء الأخرى مرفوضة. فرق السعر يسمح بالسعر السالب.

## الأسطر 18–23

```python
def implied_prices(predicted: np.ndarray, current: np.ndarray, target: str) -> np.ndarray:
    if target == "price_change":
        return current + predicted
    if target == "simple_return":
        return current * (1 + predicted)
    raise ValueError(f"Unknown target: {target}")
```

implied_prices تعكس التحويل: current+predicted للتغير أو current×(1+predicted) للعائد؛ تعيد خطأ للاسم المجهول. لا تقيد التنبؤات بموجب أو بنطاق السعر.

## الأسطر 26–27

```python
def transformed_windows(windows: WindowDataset, target: str) -> WindowDataset:
    return replace(windows, y=target_values(windows, target))
```

transformed_windows تعيد نسخة WindowDataset مع y محول، دون تغيير المصفوفة الأصلية عمداً؛ الحقول الأخرى مشتركة ما لم تنسخ منفصلة.

## الأسطر 30–41

```python
def walk_forward_partitions(windows: WindowDataset, folds: int) -> list[dict]:
    validation_size = len(windows.partitions["validation"])
    partitions = []
    for test in np.array_split(windows.partitions["test"], folds):
        cutoff = int(test[0])
        training_end = cutoff - validation_size
        if training_end < 30:
            raise ValueError("Insufficient pre-fold training history")
        partition = {"train": np.arange(training_end), "validation": np.arange(training_end, cutoff), "test": test}
        assert windows.targets[partition["validation"][-1]] <= windows.origins[test[0]]
        partitions.append(partition)
    return partitions
```

walk_forward_partitions تقسم اختباراً إلى folds متتالية، وتأخذ حجم التحقق الأصلي وتستخدم التاريخ السابق للكتلة: تدريب حتى cutoff−validation_size وتحقق بعده. تشترط 30 تدريباً وتؤكد أن آخر تسمية تحقق معروفة بحلول أول أصل اختبار. لاحقاً قد يستفاد من تسميات اختبار أسبق عند توافرها. زيادة folds على حجم الاختبار قد تخلق كتلة فارغة ويتعذر test[0].

## الأسطر 44–54

```python
def naive_predictions(windows: WindowDataset, target: str) -> dict[str, np.ndarray]:
    transformed = target_values(windows, target)
    training = transformed[windows.partitions["train"]]
    test = windows.partitions["test"]
    majority = 1 if np.sum(training > 0) >= np.sum(training < 0) else -1
    nonzero = np.abs(training[training != 0])
    magnitude = float(np.median(nonzero)) if len(nonzero) else 0.0
    if np.any(test < 1):
        raise ValueError("Last-observed baseline requires a prior known target")
    assert (windows.targets[test - 1] <= windows.origins[test]).all()
    return {"Zero": np.zeros(len(test)), "TrainMean": np.full(len(test), np.mean(training)), "LastObservedChangeOrReturn": transformed[test - 1], "TrainMajorityDirectionMedianMagnitude": np.full(len(test), majority * magnitude)}
```

naive_predictions تحسب هدف التدريب وتستخرج إشارة الأغلبية مع تعادل لصالح +1 والوسيط للمقادير غير الصفرية، وتفحص توافر الهدف السابق لكل اختبار. تعيد صفراً ومتوسط التدريب والتغير السابق وإشارة الأغلبية مضروبة بوسيط المقدار؛ صفر التغير يطابق Persistence بعد إعادة السعر. لا تعيد ملاءمة هذه الثوابت يومياً ضمن كتلة اختبار.
