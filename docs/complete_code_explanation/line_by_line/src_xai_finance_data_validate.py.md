# شرح `src/xai_finance/data/validate.py`

بصمة المصدر SHA-256: `454cd1ccd21e3d8437714df3ae9b95df7b2f8762935e8a13173a3058c1bc0488`.

اقتباسات من المصدر؛ الفراغات للتنسيق. الوصف لا يعني تنفيذ التنزيل.

## الأسطر 1–2

```python
import numpy as np
import pandas as pd
```

يستورد NumPy وpandas مكتبتين خارجيتين للتحقق من القيم والفهرس والجدول.

## الأسطر 5–8

```python
def validate_prices(prices: pd.DataFrame, frequency: str) -> pd.DataFrame:
    required = ["close"] if frequency == "monthly" else ["open", "high", "low", "close", "adj_close", "volume"]
    if not set(required).issubset(prices.columns):
        raise ValueError(f"Missing required columns: {set(required) - set(prices.columns)}")
```

validate_prices تستقبل جدولاً وتردداً وتحدد الأعمدة المطلوبة: close للشهري وإلا OHLC وadj_close وvolume؛ ترفع ValueError مع أسماء الأعمدة الناقصة إن لم توجد. لا تتحقق من أن قيمة frequency واحدة من قيم معروفة هنا.

## الأسطر 9–12

```python
    if not isinstance(prices.index, pd.DatetimeIndex) or prices.index.hasnans:
        raise ValueError("A non-null DatetimeIndex is required")
    if not prices.index.is_monotonic_increasing or prices.index.has_duplicates:
        raise ValueError("Dates must be unique and strictly chronological")
```

تتطلب DatetimeIndex دون تواريخ ناقصة، ثم ترتيباً تصاعدياً دون تكرار. بذلك يكون التسلسل صارماً مع اجتماع الشرطين؛ لا يفحص هذا وجود كل جلسة تداول متوقعة.

## الأسطر 13–16

```python
    if not np.isfinite(prices[required].to_numpy(dtype=float)).all():
        raise ValueError("Unresolved missing or infinite observations")
    if frequency == "daily":
        validate_ohlc(prices)
```

تحول الأعمدة المطلوبة إلى أعداد وتتحقق من انتهاء جميعها ثم تستدعي validate_ohlc لليومي. فشل التحويل أو وجود نقص أو لانهاية يوقف التنفيذ.

## الأسطر 17–19

```python
    if len(prices) < 100:
        raise ValueError("At least 100 genuine observations required")
    return prices
```

تطلب 100 مشاهدة على الأقل وتعيد جدول الأسعار نفسه؛ لا تنسخ أو تستكمل السجلات الناقصة.

## الأسطر 22–26

```python
def validate_ohlc(prices: pd.DataFrame) -> None:
    high_ok = prices["high"] + 1e-6 >= prices[["open", "close", "low"]].max(axis=1)
    low_ok = prices["low"] - 1e-6 <= prices[["open", "close", "high"]].min(axis=1)
    if not (high_ok & low_ok).all():
        raise ValueError("OHLC ordering is inconsistent")
```

validate_ohlc تتحقق لكل صف أن high لا يقل عن أعلى open وclose وlow وأن low لا يتجاوز أدناها، بتسامح 1e-6. إن فشل أي صف ترفع ValueError؛ الاختبار للاتساق ولا يثبت صحة السعر من المزود.

## الأسطر 27–28

```python
    if (prices["volume"] < 0).any() or (prices["close"] == 0).any():
        raise ValueError("Negative volume or zero close cannot be processed")
```

ترفض حجماً سالباً أو close يساوي صفراً لأن الحجم اللوغاريتمي ونسبة التعديل يحتاجان قيماً قابلة للمعالجة. لا ترفض كل سعر سالب بصورة عامة.
