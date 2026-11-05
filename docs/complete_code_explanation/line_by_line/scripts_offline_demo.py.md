# شرح `scripts/offline_demo.py`

بصمة المصدر SHA-256: `80d8c4d43d91a613b4209ea650894135e947a9330b45a6b0788783044c138595`.

وصف ثابت؛ لم تُشغّل السكربتات.

## الأسطر 1–3

```python
from pathlib import Path
import subprocess
import sys
```

Path وsubprocess وsys قياسية لتحديد الملفات وتشغيل العمليات.

## الأسطر 5–9

```python
ROOT = Path(__file__).resolve().parents[1]
python = ROOT / ".demo_venv/Scripts/python.exe"
if not python.exists():
    subprocess.run([sys.executable, str(ROOT / "scripts/setup_offline.py")], cwd=ROOT, check=True)
subprocess.run([str(python), str(ROOT / "scripts/launch_demo.py"), *sys.argv[1:]], cwd=ROOT, check=True)
```

يحدد Python في .demo_venv؛ إذا غاب ينفذ setup_offline باستخدام Python الحالي مع check=True، ثم ينفذ launch_demo بالبيئة والوسائط. قد ينشئ بيئة ويشغل خادماً؛ لا يفحص وجود كل اعتماد بمجرد وجود المفسر.
