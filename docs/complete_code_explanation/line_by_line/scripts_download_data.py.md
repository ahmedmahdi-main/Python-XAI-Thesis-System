# شرح `scripts/download_data.py`

بصمة المصدر SHA-256: `ba95c0c7f7ffc4743e4e23751218a222ea3ed59e79dcc658e2f838226bf9b3eb`.

الاقتباسات من الملف؛ لم تُشغّل السكربتات أو تجاربها.

## الأسطر 1–2

```python
from xai_finance.config import load_config
from xai_finance.io.data_sources import download_all
```

يستورد load_config وdownload_all داخليتين.

## الأسطر 4–4

```python
download_all(load_config("configs/full_experiment.yaml"))
```

عند تنفيذ الملف أو استيراده يستدعي تنزيل الأصول وفق full_experiment.yaml؛ لقطة موجودة تمر بالتحقق كما في download_all. قد يحدث طلب شبكة وكتابة ولم ينفذ هنا.
