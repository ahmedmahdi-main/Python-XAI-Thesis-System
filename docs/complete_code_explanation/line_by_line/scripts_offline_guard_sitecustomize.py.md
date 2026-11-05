# شرح `scripts/offline_guard/sitecustomize.py`

بصمة المصدر SHA-256: `a3896b513d9353603084ef86386666a57ad1f35d1a32b37c2414af26d7001b5a`.

وصف ثابت؛ لم تُشغّل السكربتات.

## الأسطر 1–4

```python
"""Test-only network guard, enabled explicitly by XAI_TEST_OFFLINE=1."""

import os
import socket
```

سلسلة توثق أنه حارس اختبار اختياري؛ os وsocket قياسيتان.

## الأسطر 6–10

```python
if os.environ.get("XAI_TEST_OFFLINE") == "1":
    _connect = socket.socket.connect
    _connect_ex = socket.socket.connect_ex
    _getaddrinfo = socket.getaddrinfo
    _local = {"localhost", "127.0.0.1", "::1", None}
```

فقط عند XAI_TEST_OFFLINE=1 يحفظ دوال الاتصال وحل الأسماء الأصلية ويحدد أسماء loopback المقبولة. يحتاج تحميل sitecustomize من مسار Python المناسب.

## الأسطر 12–14

```python
    def _check(host):
        if host not in _local:
            raise OSError(f"Offline acceptance test denied external network: {host}")
```

_check ترفض host خارج المجموعة بخطأ OSError؛ السماح بالأسماء المحددة لا يثبت حجب كل وسائل الشبكة الممكنة.

## الأسطر 16–24

```python
    def connect(connection, address):
        if isinstance(address, tuple):
            _check(address[0])
        return _connect(connection, address)

    def connect_ex(connection, address):
        if isinstance(address, tuple):
            _check(address[0])
        return _connect_ex(connection, address)
```

connect وconnect_ex تفحصان عنوان tuple ثم تفوضان الاتصال الأصلي؛ عناوين غير tuple لا يفحصها هذا الشرط.

## الأسطر 26–32

```python
    def getaddrinfo(host, *args, **kwargs):
        _check(host)
        return _getaddrinfo(host, *args, **kwargs)

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.getaddrinfo = getaddrinfo
```

getaddrinfo يفحص المضيف ويفوض الأصل ثم يستبدل ثلاث دوال socket داخل العملية. هذا حارس اختبار لواجهات محددة لا جدار حماية شامل.
