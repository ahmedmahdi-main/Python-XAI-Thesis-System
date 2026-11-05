# شرح `src/xai_finance/data/features.py`

بصمة المصدر SHA-256: `dca14d81cf7b8d7bf7702e5507934a37b6a92113c9ea4447829d9e5bcbd2110a`.

الاقتباسات من المصدر الفعلي؛ الأسطر الفارغة للتنسيق. لا ينفذ هذا الشرح التدريب أو يعدل البيانات.

## الأسطر 1–2

```python
import numpy as np
import pandas as pd
```

يستورد NumPy للعمليات العددية والقيم غير المنتهية، وpandas للسلاسل والجداول. كلاهما مكتبتان خارجيتان.

## الأسطر 5–6

```python
def relative_strength(close: pd.Series) -> pd.Series:
    changes = close.diff()
```

relative_strength تستقبل سلسلة إغلاق وتعيد سلسلة RSI؛ diff يحسب تغير كل رصد عن السابق، فتكون البداية ناقصة.

## الأسطر 7–8

```python
    gains = changes.clip(lower=0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    losses = (-changes.clip(upper=0)).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
```

يفصل التغيرات الموجبة والخسائر المطلقة بالقص ثم يحسب متوسطاً أُسّياً بمعامل 1/14 وadjust=False وبعد 14 قيمة على الأقل. هذا تهيئة EWM في pandas ولا يلزم افتراض تطابق كل تفاصيلها مع كل تعريف آخر لـ RSI.

## الأسطر 9–11

```python
    ratio = gains / losses.replace(0, np.nan)
    rsi = 100 - 100 / (1 + ratio)
    return rsi.mask((losses == 0) & (gains > 0), 100).mask((losses == 0) & (gains == 0), 50)
```

يقسم متوسط المكاسب على الخسائر بعد استبدال صفر المقام بـ NaN، ثم يحسب 100−100/(1+ratio). يعالج غياب الخسائر مع مكاسب بـ100 وغياب الاثنين بـ50؛ بيانات أخرى ناقصة تبقى ناقصة.

## الأسطر 14–16

```python
def features(prices: pd.DataFrame, frequency: str) -> pd.DataFrame:
    close = prices["close"] if frequency == "monthly" else prices["adj_close"]
    engineered = pd.DataFrame({"close": close}, index=prices.index)
```

features تستقبل جدول الأسعار والتردد وتنشئ جدولاً بمحاذاة فهرس المدخل؛ تستخدم close للشهري وadj_close لأي قيمة أخرى. مسار الاستدعاء المعتاد train_asset يمرر تردد بيان المصدر.

## الأسطر 17–21

```python
    if frequency == "daily":
        adjustment = prices["adj_close"] / prices["close"]
        for column in ["open", "high", "low"]:
            engineered[column] = prices[column] * adjustment
        engineered["log_volume"] = np.log1p(prices["volume"])
```

للبيانات اليومية يحسب معامل تعديل الإغلاق ثم يضرب open وhigh وlow فيه، ويضيف log1p(volume) أي log(1+volume). القسمة على صفر أو قيم غير صالحة ستعالج كقيم غير منتهية أو مفقودة لاحقاً.

## الأسطر 22–23

```python
    engineered["sma_5"] = close.rolling(5).mean()
    engineered["sma_20"] = close.rolling(20).mean()
```

يحسب المتوسطين المتحركين البسيطين لآخر 5 و20 رصداً: SMAₙ(t)=Σclose(t−k)/n. بداية كل نافذة الكاملة ناقصة.

## الأسطر 24–26

```python
    engineered["ema_12"] = close.ewm(span=12, adjust=False, min_periods=12).mean()
    engineered["ema_26"] = close.ewm(span=26, adjust=False, min_periods=26).mean()
    engineered["rsi_14"] = relative_strength(close)
```

يحسب EMA لفترتي 12 و26 مع حد أدنى مطابق لكل فترة، ويستدعي relative_strength على الإغلاق. EMA وزن أسي للماضي لا متوسطاً بسيطاً.

## الأسطر 27–28

```python
    engineered["macd"] = engineered["ema_12"] - engineered["ema_26"]
    engineered["macd_signal"] = engineered["macd"].ewm(span=9, adjust=False, min_periods=9).mean()
```

MACD هو الفرق بين EMA12 وEMA26؛ signal متوسط أسي لـ MACD بفترة 9 ويتطلب تسع قيم صالحة.

## الأسطر 29–31

```python
    dispersion = close.rolling(20).std(ddof=0)
    engineered["bollinger_upper"] = engineered["sma_20"] + 2 * dispersion
    engineered["bollinger_lower"] = engineered["sma_20"] - 2 * dispersion
```

الانحراف المعياري لنافذة 20 يستخدم ddof=0، ثم الحد الأعلى SMA20+2σ والأدنى SMA20−2σ. لا يشير تجاوز الحد تلقائياً إلى علاقة سببية.

## السطر 32

```python
    return return_features(engineered, close).replace([np.inf, -np.inf], np.nan).dropna()
```

يستدعي return_features لإضافة السمات ثم يستبدل ±inf بـ NaN ويحذف كل صف يحوي نقصاً ويعيد الجدول. قد يحذف أكثر من فترة التهيئة؛ لا يملأ فجوات.

## الأسطر 35–39

```python
def return_features(engineered: pd.DataFrame, close: pd.Series) -> pd.DataFrame:
    returns = close.pct_change(fill_method=None)
    engineered["return_1"] = returns
    engineered["return_lag_1"] = returns.shift(1)
    engineered["return_lag_5"] = returns.shift(5)
```

return_features تعدل جدول engineered الممرر وتعيده. pct_change دون ملء تحسب c_t/c_(t−1)−1؛ return_1 القيمة الحالية، واللاحقتان تؤخرانها رصداً أو خمسة رصود.

## الأسطر 40–43

```python
    engineered["volatility_20"] = returns.rolling(20).std(ddof=0)
    engineered["momentum_10"] = close - close.shift(10)
    engineered["trailing_return_20"] = close.pct_change(20, fill_method=None)
    return engineered
```

تضيف تقلب العوائد على 20 رصداً بانحراف ddof=0، وزخم فرق الإغلاق عن عشرة رصود، والعائد النسبي عبر 20 رصداً؛ ثم تعيد الجدول المعدل. الفترات هي رصود، وليست بالضرورة أيام تقويمية.
