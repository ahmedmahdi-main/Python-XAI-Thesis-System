# شرح `scripts/diagnose_validation_replay.py`

بصمة المصدر SHA-256: `85b81348e6c1526984648cf03650f24589fca23b5af0d388fcbccf951bd50ce1`.

لم يُشغّل السكربت في جلسة التوثيق.

## الأسطر 1–12

```python
"""Measure cross-device error before choosing a precision-aware replay criterion."""
import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from xai_finance.models.lstm_model import load_lstm
from xai_finance.pipelines.train import load_windows
from xai_finance.seed import seed_experiment
from xai_finance.storage import read_json, write_json
```

توثيق واستيرادات قراءة ونماذج LSTM ونوافذ وبذور وتخزين؛ يتطلب torch وCUDA ضمن load_lstm.

## الأسطر 15–20

```python
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    destination = parser.parse_args().folder.resolve()
    seed_experiment(42)
    diagnostics = []
```

main تقرأ مجلد التحقق وتضبط البذرة وتبدأ نتائج التشخيص.

## الأسطر 21–28

```python
    for path in sorted((destination / "experiments").rglob("design.json")):
        design = read_json(path)
        windows = load_windows(Path(design["input_windows_source"]).parent)
        with np.load(path.parent / "target_and_partitions.npz") as saved:
            fixture = windows.flat[saved["test"]]
        table = pd.read_csv(path.parent / "predictions.csv", float_precision="round_trip")
        recorded = table.loc[table.model == "LSTM", "predicted_target"].to_numpy()
        scalers = joblib.load(path.parent / "LSTM/scalers.joblib")
```

تمر على design.json للمهام وتحمل نوافذ المصدر وفهارس الاختبار والتنبؤ المحفوظ والمعايير؛ joblib ينبغي تحميله من مصدر موثوق.

## الأسطر 29–34

```python
        cpu = load_lstm(path.parent / "LSTM", scalers, "cpu").predict(fixture)
        gpu = load_lstm(path.parent / "LSTM", scalers, "cuda").predict(fixture)
        np.testing.assert_array_equal(gpu, recorded)
        diagnostics.append({**{name: design[name] for name in ["asset", "target", "design", "fold"]}, "cuda_replay_bitwise_equal": bool(np.array_equal(gpu, recorded)), "cpu_max_abs_error_target_units": float(np.max(np.abs(cpu - recorded))), "training_target_scale": float(scalers.target.scale_[0]), "cpu_max_error_training_std_units": float(np.max(np.abs(cpu - recorded)) / scalers.target.scale_[0])})
    write_json(destination / "cross_device_diagnostics.json", diagnostics)
    print(pd.DataFrame(diagnostics).to_string(index=False))
```

تحسب التنبؤ ذاته بإعادة تحميل CPU وCUDA وتفرض تطابق GPU والمحفوظه بتاً بت، وتسجل أقصى خطأ CPU بالوحدة الأصلية ومعيار التدريب ثم تكتب JSON وتطبع. يتطلب CUDA ولا يثبت تطابق أجهزة أخرى؛ لم يُنفذ هنا.

## الأسطر 37–38

```python
if __name__ == "__main__":
    main()
```

حارس التشغيل يستدعي main.
