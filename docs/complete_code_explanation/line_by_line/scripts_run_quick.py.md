# شرح `scripts/run_quick.py`

بصمة المصدر SHA-256: `363667f99ecbd1269c19f654f69fa87971cd41d6c4053cd7d17fa0a6fc30fdca`.

تفسير مقابل المصدر، لم تُشغّل الأوامر الموثقة.

## الأسطر 1–4

```python
import os
from pathlib import Path
import subprocess
import sys
```

os وPath وsubprocess وsys مكتبات قياسية للمسارات وبيئة وتشغيل عملية Python.

## الأسطر 6–9

```python
ROOT = Path(__file__).resolve().parents[1]
os.environ["PYTHONHASHSEED"] = "42"
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
subprocess.run([sys.executable, "-m", "xai_finance.cli", "all", "--config", "configs/quick_demo.yaml"], cwd=ROOT, check=True)
```

يستخرج الجذر من موقع السكربت ويعين PYTHONHASHSEED وCUBLAS لعملية الابن ثم يشغل CLI all بتهيئة quick_demo وفي الجذر؛ check=True يرفع خطأ عند فشل الأمر. هذه نقطة دخول ذات آثار تنزيل وتدريب وتفسير وتقارير ولم تشغل هنا.
