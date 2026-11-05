# شرح `scripts/replicate_validation_lstm.py`

بصمة المصدر SHA-256: `d95bd5ef5cb381409e38ba355d9822eff275869dcd1b989803a3cd7317eae2c3`.

لم يُشغّل السكربت في جلسة التوثيق.

## الأسطر 1–14

```python
"""Repeat one CUDA fit using the recorded configuration; never overwrite a fit."""
import argparse
from pathlib import Path

import joblib
import numpy as np
from threadpoolctl import threadpool_limits

from xai_finance.config import ROOT
from xai_finance.models.lstm_model import fit_lstm, load_lstm
from xai_finance.pipelines.train import load_windows
from xai_finance.seed import seed_experiment
from xai_finance.storage import read_json, write_json
from xai_finance.validation.design import transformed_windows
```

توثيق واستيرادات إعداد وإعادة تدريب LSTM وقراءة النوافذ والهدف والحفظ؛ هذا سكربت تجربة لا توثيق فقط.

## الأسطر 17–28

```python
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    arguments = parser.parse_args()
    destination = arguments.folder.resolve()
    folder = destination / "experiments/fixed_split/price_change/AAPL_fold0"
    design = read_json(folder / "design.json")
    protocol = read_json(destination / "protocol.json")
    windows = transformed_windows(load_windows(ROOT / "artifacts/runs" / protocol["original_run"] / "AAPL"), "price_change")
    output = destination / "determinism_replication"
    output.mkdir(exist_ok=False)
    seed_experiment(protocol["seed"])
```

main تقرأ الوجهة والتصميم والبروتوكول وتحول نوافذ AAPL إلى فرق السعر وتخلق مجلد تكرار exist_ok=False وتضبط البذرة. يمنع وجود المجلد إعادة استخدامه.

## الأسطر 29–35

```python
    with threadpool_limits(limits=4):
        predictor, metadata = fit_lstm(windows, design["configuration"], output)
    joblib.dump(predictor.scalers, output / "scalers.joblib")
    reference_scalers = joblib.load(folder / "LSTM/scalers.joblib")
    for name in ["inputs", "target"]:
        for attribute in ["mean_", "scale_", "var_"]:
            np.testing.assert_array_equal(getattr(getattr(predictor.scalers, name), attribute), getattr(getattr(reference_scalers, name), attribute))
```

تدرب LSTM مع حدود الخيوط وتحفظ scalers وتقارن متوسطاتها ومقاييسها وتباينها مع المرجع. إعادة التدريب تغير آثاراً ولم تُنفذ هنا.

## الأسطر 36–45

```python
    reference = load_lstm(folder / "LSTM", reference_scalers, "cuda" if predictor.device.type == "cuda" else "cpu")
    fixture = windows.flat[windows.partitions["test"]]
    repeated, previous = predictor.predict(fixture), reference.predict(fixture)
    np.testing.assert_array_equal(repeated, previous)
    reference_history = read_json(folder / "LSTM/history.json")
    repeated_history = read_json(output / "history.json")
    assert len(reference_history) == len(repeated_history)
    for before, after in zip(reference_history, repeated_history):
        for key in ["epoch", "train_loss", "validation_loss"]:
            assert before[key] == after[key]
```

تحمل مرجعاً على نوع جهاز التكرار وتقارن تنبؤات الاختبار بتاً بت ثم تقارن طول التاريخ وكل epoch وخسارة تدريب وتحقق. لا تقارن الزمن وتفترض إمكانية إعادة إنتاج البيئة.

## الأسطر 46–47

```python
    write_json(output / "verification.json", {"training_metadata": metadata, "test_n": len(fixture), "predictions_bitwise_identical": bool(np.array_equal(repeated, previous)), "max_abs_prediction_difference": float(np.max(np.abs(repeated - previous))), "epoch_losses_identical": True, "scope": "One AAPL price-change LSTM repeat on same hardware/software; not a multi-seed robustness study"})
    print("Repeated LSTM: all epoch losses and 271 predictions bitwise identical")
```

تكتب إيصال المقارنة وتطبع النتيجة؛ النطاق تجربة AAPL واحدة على بيئة محددة، لا برهان استقرار متعدد البذور.

## الأسطر 50–51

```python
if __name__ == "__main__":
    main()
```

حارس التنفيذ يستدعي main.
