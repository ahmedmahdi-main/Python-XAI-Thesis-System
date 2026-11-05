# شرح `scripts/run_full.py`

بصمة المصدر SHA-256: `92057d2f60510454413260b8774ac73016f435ce3f25dfebdd3fd59c71460be6`.

تفسير مقابل المصدر، لم تُشغّل الأوامر الموثقة.

## الأسطر 1–4

```python
import os
from pathlib import Path
import subprocess
import sys
```

os وPath وsubprocess وsys قياسية لاختيار الجذر وتشغيل عملية فرعية.

## الأسطر 6–9

```python
ROOT = Path(__file__).resolve().parents[1]
os.environ["PYTHONHASHSEED"] = "42"
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
subprocess.run([sys.executable, "-m", "xai_finance.cli", "all", "--config", "configs/full_experiment.yaml"], cwd=ROOT, check=True)
```

يعين جذر المشروع وبذرة الهاش وإعداد CUBLAS ويشغل CLI all مع full_experiment.yaml؛ check=True يكشف فشل العملية. تنفيذ السكربت يجري سير التجربة الكامل ولم يحدث هنا.
