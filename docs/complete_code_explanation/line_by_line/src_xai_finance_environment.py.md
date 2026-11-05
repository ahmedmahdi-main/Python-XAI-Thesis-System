# شرح `src/xai_finance/environment.py`

بصمة المصدر SHA-256: `e2a6e042ad20127ec074dc8c2d05d30daa074c2d0f0e4f1d809ea8ca156879ed`.

تفسير مقابل المصدر، لم تُشغّل الأوامر الموثقة.

## الأسطر 1–8

```python
import json

import torch

from xai_finance.config import ROOT
from xai_finance.pipelines.train import software_environment
from xai_finance.seed import seed_experiment, select_device
from xai_finance.storage import write_json
```

json قياسية وtorch خارجية؛ ROOT وsoftware_environment والبذرة واختيار الجهاز وwrite_json من المشروع.

## الأسطر 11–19

```python
def verify_environment() -> None:
    seed_experiment(42)
    device, reason = select_device("auto")
    network = torch.nn.LSTM(8, 16, batch_first=True).to(device)
    output, _ = network(torch.randn(8, 30, 8, device=device))
    output.square().mean().backward()
    if not torch.isfinite(output).all():
        raise FloatingPointError("Hardware LSTM diagnostic nonfinite")
    report = {**software_environment(), "device": str(device), "reason": reason, "torch_cuda": torch.version.cuda, "cuda_available": torch.cuda.is_available(), "lstm_probe_finite": True, "scope": "random tensor hardware diagnostic, not financial results"}
```

verify_environment تثبت بذرة 42 وتختار الجهاز، وتبني LSTM تشخيصية بثماني سمات و16 مخفية على مدخل عشوائي 8×30×8 وتجري backward على متوسط مربع الخرج، وتتحقق من finiteness للخرج ثم تجمع معلومات البيئة. هذا اختبار عتاد عشوائي لا نتيجة مالية ولا يتحقق صراحة من finiteness كل تدرج.

## الأسطر 20–24

```python
    if device.type == "cuda":
        report["gpu_name"] = torch.cuda.get_device_name(0)
        report["vram_bytes"] = torch.cuda.get_device_properties(0).total_memory
    write_json(ROOT / "artifacts/environment/current.json", report)
    print(json.dumps(report, indent=2))
```

تضيف اسم GPU وذاكرته عند CUDA وتكتب التقرير في artifacts/environment/current.json وتطبعه؛ لها أثر كتابة وتغير البذور ولم تشغل هنا.
