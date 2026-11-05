# شرح `scripts/launch_demo.py`

بصمة المصدر SHA-256: `dd79873ce8b441b06505e590f18152d3b5e7ccf54e2960d9d0ce59ed9dfc35b2`.

وصف ثابت؛ لم تُشغّل السكربتات.

## الأسطر 1–4

```python
import os
from pathlib import Path
import subprocess
import sys
```

مكتبات قياسية للبيئة والمسارات والعملية الفرعية والوسائط.

## الأسطر 6–8

```python
ROOT = Path(__file__).resolve().parents[1]
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
raise SystemExit(subprocess.call([sys.executable, str(ROOT / "scripts/demo_wizard.py"), "start", *sys.argv[1:]], cwd=ROOT))
```

يحدد جذر المشروع ويعطل جمع إحصاء استخدام المتصفح في Streamlit، ويشغل demo_wizard.py start بوسائط المستخدم ويعيد رمز العملية عبر SystemExit. يتغير متغير البيئة وتبدأ عملية عند التنفيذ أو الاستيراد.
