# شرح `src/xai_finance/seed.py`

بصمة المصدر SHA-256: `6cc9044fc7eae48d3cfb6580a0cc677faf6143a26fcc4b1c8053df684059710b`.

تفسير مقابل المصدر، لم تُشغّل الأوامر الموثقة.

## الأسطر 1–7

```python
import os
import random

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np
import torch
```

os وrandom قياسيتان؛ يضبط setdefault إعداد CUBLAS قبل تحميل NumPy وtorch الخارجيتين ولا يغير قيمة سابقة.

## الأسطر 10–19

```python
def seed_experiment(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.set_num_threads(4)
```

seed_experiment يثبت بذور random وNumPy وTorch وCUDA، ويفرض خوارزميات حتمية، ويعطل benchmark وTF32 ويحدد أربعة خيوط. يغير الحالة العامة للعملية وقد يرفع خطأ لخوارزمية غير حتمية؛ لا يضمن تطابقاً بين كل الإصدارات والأجهزة.

## الأسطر 22–30

```python
def select_device(requested: str) -> tuple[torch.device, str]:
    if requested == "cpu":
        return torch.device("cpu"), "CPU explicitly requested"
    if requested not in {"auto", "cuda"}:
        raise ValueError("device must be auto, cuda or cpu")
    if torch.cuda.is_available():
        try:
            torch.ones(1, device="cuda").sum().item()
            return torch.device("cuda"), "CUDA allocation verified"
```

select_device تقبل cpu أو auto أو cuda. تعيد CPU فور طلبه، وترفض قيمة غير معروفة، وتختبر تخصيص CUDA وحساباً صغيراً إن كان متاحاً قبل إرجاع الجهاز والسبب.

## الأسطر 31–37

```python
        except RuntimeError as failure:
            if requested == "cuda":
                raise
            return torch.device("cpu"), f"CUDA runtime failure: {failure}"
    if requested == "cuda":
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is False")
    return torch.device("cpu"), "CUDA unavailable; automatic CPU fallback"
```

عند فشل CUDA تعيد CPU في auto أو تعيد رفع الاستثناء للطلب الصريح؛ وعند غيابه ترفض cuda وتختار CPU لـ auto. الاختبار لا يضمن ذاكرة كافية للتدريب كاملاً.
