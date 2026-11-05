# شرح `scripts/audit_reconstruction_precision.py`

بصمة المصدر SHA-256: `de19a61fb8a087653e0a96164a00d338734e7a9f5ebedecce00b58ca97dde810`.

لم يُشغّل السكربت في جلسة التوثيق.

## الأسطر 1–10

```python
"""Retain as-executed forecasts and save a separate FP64 reconstruction sensitivity."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from xai_finance.storage import sha256, write_json
from xai_finance.validation.design import implied_prices
from xai_finance.validation.statistics import evaluation_metrics
```

توثيق ومكتبات قياسية وخارجية لتدقيق حساسية FP64، ووظائف التحويل والمقاييس والبصمة الداخلية.

## الأسطر 13–18

```python
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    destination = parser.parse_args().folder.resolve()
    predictions = pd.read_csv(destination / "new_predictions.csv", float_precision="round_trip")
    comparisons, corrected_tables, metric_rows = [], [], []
```

main تقرأ مجلد التحقق ثم تنبؤاته المحفوظة بدقة round_trip وتبدأ قوائم المقارنة والجداول.

## الأسطر 19–24

```python
    for keys, group in predictions.groupby(["design", "target", "asset", "model"], sort=False):
        group = group.sort_values("target_date").copy()
        corrected = group.copy()
        corrected["as_executed_predicted_price"] = group.predicted_price
        corrected["predicted_price"] = implied_prices(group.predicted_target.to_numpy(dtype=np.float64), group.current_price.to_numpy(dtype=np.float64), keys[1])
        corrected_tables.append(corrected)
```

لكل تصميم وهدف وأصل ونموذج ترتب التواريخ وتنسخ الجدول وتحفظ التنبؤ الأصلي وتعيد تركيب السعر بعد تحويل الهدف والسعر الحالي إلى float64. هذه حساسية حسابية منفصلة لا تعيد تدريباً.

## الأسطر 25–28

```python
        before, after = evaluation_metrics(group), evaluation_metrics(corrected)
        identity = dict(zip(["design", "target", "asset", "model"], keys))
        metric_rows.append({**identity, **after})
        comparisons.append({**identity, "max_price_difference": float(np.max(np.abs(corrected.predicted_price - group.predicted_price))), "as_executed_rmse": before["rmse"], "float64_rmse": after["rmse"], "rmse_difference": after["rmse"] - before["rmse"], "direction_predictions_changed": int(np.sum(np.sign(group.predicted_price - group.current_price) != np.sign(corrected.predicted_price - corrected.current_price)))})
```

تحسب مقاييس قبل وبعد وتجمع الهوية وأعظم فرق سعر وفرق RMSE وعدد تغيرات إشارة التوقع. الحساب يقرأ التنبؤ المحفوظ ولا يثبت جودة النموذج.

## الأسطر 29–33

```python
    pd.DataFrame(comparisons).to_csv(destination / "reconstruction_precision_comparison.csv", index=False)
    pd.DataFrame(metric_rows).to_csv(destination / "float64_reconstructed_metrics.csv", index=False)
    pd.concat(corrected_tables, ignore_index=True).to_csv(destination / "float64_reconstructed_predictions.csv", index=False)
    write_json(destination / "reconstruction_precision_provenance.json", {"original_predictions_sha256": sha256(destination / "new_predictions.csv"), "target_values_unchanged": True, "models_retrained": False, "algorithm": "Cast saved target prediction to float64 before 1+r and price reconstruction; as-executed files untouched", "as_executed_lstm_target_dtype": "float32", "reason": "Native float32 1+r rounds before multiplication by float64 current price; separate numerical sensitivity, not a replacement experiment"})
    print(pd.DataFrame(comparisons).query("max_price_difference > 1e-8").to_string(index=False))
```

تكتب ملفات مقارنة وتنبؤات ومقاييس FP64 منفصلة مع بصمة الأصل والمنشأ وتطبع الفروق؛ التنفيذ يعدل آثار التحقق ولم يُشغّل هنا.

## الأسطر 36–37

```python
if __name__ == "__main__":
    main()
```

حارس التنفيذ يستدعي main.
