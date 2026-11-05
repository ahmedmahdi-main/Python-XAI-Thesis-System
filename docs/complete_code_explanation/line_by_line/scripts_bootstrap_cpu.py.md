# شرح `scripts/bootstrap_cpu.py`

بصمة المصدر SHA-256: `a568f19f82e8f9e133d83b6bbf27b52b1982f98147d4d1b78436ce6e3d83fb9a`.

وصف ثابت؛ لم تُشغّل السكربتات.

## الأسطر 1–6

```python
"""Find an already-installed x64 Python 3.12; never download a runtime implicitly."""

import os
from pathlib import Path
import subprocess
import sys
```

توثيق البحث المحلي عن Python 3.12 x64، واستيرادات البيئة والمسارات والعمليات القياسية.

## الأسطر 8–11

```python
ROOT = Path(__file__).resolve().parents[1]
check = "import sys,struct; assert sys.version_info[:2]==(3,12) and struct.calcsize('P')==8"
candidates = [Path(os.environ["XAI_PYTHON"])] if os.environ.get("XAI_PYTHON") else []
candidates.append(Path(sys.executable))
```

يحدد الجذر وسلسلة تحقق لإصدار 3.12 وحجم مؤشر 8 بايت، ويبدأ قائمة المرشحين من XAI_PYTHON إن وجد ثم Python الحالي.

## الأسطر 12–17

```python
for variable in ["APPDATA", "LOCALAPPDATA"]:
    if os.environ.get(variable):
        folder = Path(os.environ[variable]) / "uv/python"
        candidates.extend(sorted(folder.glob("cpython-3.12*-windows-x86_64-none/python.exe"), reverse=True))
if os.environ.get("UV_PYTHON_INSTALL_DIR"):
    candidates.extend(sorted(Path(os.environ["UV_PYTHON_INSTALL_DIR"]).glob("cpython-3.12*-windows-x86_64-none/python.exe"), reverse=True))
```

يبحث في مجلدات uv تحت APPDATA وLOCALAPPDATA وفي UV_PYTHON_INSTALL_DIR عند وجودها عن Python Windows x86_64، ويرتب النتائج تنازلياً.

## الأسطر 18–23

```python
for python in dict.fromkeys(candidates):
    if python.is_file() and subprocess.run([str(python), "-c", check], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        raise SystemExit(subprocess.call([str(python), str(ROOT / "scripts/demo_wizard.py"), "setup", *sys.argv[1:]], cwd=ROOT))
print("Windows x64 Python 3.12 was not found. Install it for your user, then rerun SETUP_DEMO.bat.")
print("If it is installed in a custom location, set XAI_PYTHON to its full python.exe path.")
raise SystemExit(1)
```

يزيل تكرار المرشحين بترتيب الإدراج ويشغل تحقق الإصدار على كل ملف؛ عند النجاح يشغل wizard setup ويعيد رمزه. إن لم يوجد يطبع إرشادات ويخرج 1؛ لا ينزل Python تلقائياً.
