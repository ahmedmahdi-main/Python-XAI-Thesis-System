# شرح `scripts/offline_smoke.py`

بصمة المصدر SHA-256: `b8fc7ee98de68c6d372cf9ca5c55ebbb3eb8df494be57f8fc7f1120f54a348ce`.

لم يُشغّل السكربت في جلسة التوثيق.

## الأسطر 1–10

```python
"""Block external Python sockets while exercising the saved-artifact dashboard."""

from pathlib import Path
import json
import socket

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
original_connect = socket.socket.connect
```

توثيق واستيرادات Path وjson وsocket وAppTest، وتحديد الجذر وحفظ دالة اتصال socket الأصلية.

## الأسطر 13–16

```python
def loopback_only(connection, address):
    if isinstance(address, tuple) and address[0] not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError(f"Offline rehearsal blocked external network: {address[0]}")
    return original_connect(connection, address)
```

loopback_only ترفض عنوان tuple غير localhost ثم تفوض الاتصال الأصلي. لا تغطي وحدها جميع طرق الشبكة أو كل أشكال العنوان.

## الأسطر 19–26

```python
socket.socket.connect = loopback_only
app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=90).run()
assert not app.exception, app.exception
assert len(app.tabs) == 8
assets = app.selectbox(key="asset").options
pointer = json.loads((ROOT / "artifacts/latest_full.json").read_text())
metadata = json.loads((ROOT / "artifacts/runs" / pointer["run_id"] / "run.json").read_text())
assert set(assets) == set(metadata["configuration"]["assets"])
```

تستبدل socket.connect في العملية وتشغل AppTest للواجهة، وتفحص غياب الاستثناء وثمانية تبويبات وتطابق خيارات الأصول مع إعداد التشغيل المحفوظ.

## الأسطر 27–35

```python
for asset in assets:
    app.selectbox(key="asset").set_value(asset).run()
    assert not app.exception, app.exception
    for model in ["LinearRegression", "RandomForest", "GradientBoosting", "LSTM"]:
        app.selectbox(key="explain_model").set_value(model).run()
        assert not app.exception, app.exception
    dates = app.selectbox(key="explanation_date").options
    app.selectbox(key="explanation_date").set_value(dates[-1]).run()
    assert not app.exception, app.exception
```

تختار كل أصل وكل نموذج تفسير وتتحقق من غياب الاستثناء، ثم تختار آخر تاريخ محسوب مسبقاً. حالة أول تاريخ تفترض الاختيار الافتراضي ولا تتحقق صراحة من جميع التواريخ.

## الأسطر 36–38

```python
receipt = {"status": "PASSED", "run_id": pointer["run_id"], "assets": assets, "models_per_asset": 4, "tabs": len(app.tabs), "date_check": "first and last precomputed dates", "external_socket_connections": "blocked", "scope": "Saved-artifact viewing only; not retraining or a browser pixel screenshot"}
(ROOT / "artifacts/tests/offline_dashboard.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
print(f"OFFLINE DASHBOARD PASS: {len(assets)} datasets, four explanation models, first/last precomputed dates, eight tabs. External sockets blocked.")
```

تكتب إيصالاً في artifacts/tests وتطبع النجاح؛ يصف العرض المحفوظ دون تدريب أو اختبار صور متصفح. لم يشغل هنا.
