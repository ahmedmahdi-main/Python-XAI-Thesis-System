# شرح `scripts/setup_offline.py`

بصمة المصدر SHA-256: `955a5ec1562e5e2e48d10c6cfbf9b126ea754cd4177b995c81c4e29e86156148`.

وصف ثابت؛ لم تُشغّل السكربتات.

## الأسطر 1–5

```python
"""Compatibility command for the CPU-only offline setup wizard."""

from pathlib import Path
import subprocess
import sys
```

سلسلة توثيق ومكتبات قياسية للمسار والعملية والوسائط.

## الأسطر 7–8

```python
ROOT = Path(__file__).resolve().parents[1]
raise SystemExit(subprocess.call([sys.executable, str(ROOT / "scripts/demo_wizard.py"), "setup", "--offline", *sys.argv[1:]], cwd=ROOT))
```

يشغّل wizard بأمر setup و--offline ووسائط المستخدم من الجذر، ويمرر رمز الخروج. قد يثبت حزم محلية؛ لم يشغل هنا.
