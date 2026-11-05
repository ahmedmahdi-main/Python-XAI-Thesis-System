# شرح `tests/test_dashboard.py`

بصمة المصدر SHA-256: `3f0c02101dd582654eb007414d60de23a2dfc0e6d48bad229bf2d8defe5767dd`.

وصف الاختبارات لا يعني أنها شُغلت في جلسة التوثيق.

## الأسطر 1–4

```python
from pathlib import Path
import shutil

from streamlit.testing.v1 import AppTest
```

Path وshutil قياسيتان وAppTest أداة اختبار Streamlit.

## الأسطر 7–15

```python
def test_missing_artifacts_shows_actionable_setup_commands(tmp_path):
    project = Path(__file__).resolve().parents[1]
    dashboard = tmp_path / "dashboard"
    dashboard.mkdir()
    shutil.copy2(project / "dashboard/app.py", dashboard / "app.py")
    app = AppTest.from_file(str(dashboard / "app.py")).run(timeout=30)
    assert not app.exception
    assert any("No saved experiment" in message.value for message in app.info)
    assert "xai_finance.cli train" in app.code[0].value
```

ينشئ مشروعاً مؤقتاً مع نسخة الواجهة دون آثار، ويشغلها ويؤكد عدم الاستثناء وظهور رسالة غياب التشغيل وأمر التدريب؛ لا يتحقق من التبويبات عند وجود بيانات.
