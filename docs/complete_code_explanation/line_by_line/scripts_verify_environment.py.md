# شرح `scripts/verify_environment.py`

بصمة المصدر SHA-256: `2af3643f81dccec4e566397fcb79b59f5f412c29fcd6c8dee05482bbef24b132`.

وصف ثابت؛ لم تُشغّل السكربتات.

## الأسطر 1–1

```python
from xai_finance.environment import verify_environment
```

يستورد تشخيص البيئة من الحزمة.

## الأسطر 3–3

```python
verify_environment()
```

يستدعي التشخيص حتى عند استيراد السكربت؛ يختبر LSTM عشوائياً ويكتب تقرير البيئة كما في الدالة، وليس نتائج مالية.
