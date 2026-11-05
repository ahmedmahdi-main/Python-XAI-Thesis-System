# شرح `src/xai_finance/io/data_sources.py`

بصمة المصدر SHA-256: `c2092e3c5dd9173fccedf3879ad4743640e7c905b4a85e8fb075c9ffadb7a042`.

اقتباسات من المصدر؛ الفراغات للتنسيق. الوصف لا يعني تنفيذ التنزيل.

## الأسطر 1–2

```python
from datetime import datetime, timezone
from io import StringIO
```

datetime وtimezone لتوثيق الاسترجاع UTC وStringIO لقراءة نص CSV؛ جميعها من المكتبة القياسية.

## الأسطر 4–6

```python
import pandas as pd
import requests
import yfinance as yf
```

pandas لمعالجة الجداول وrequests لتنزيل HTTP وyfinance لمزود Yahoo؛ مكتبات خارجية.

## الأسطر 8–10

```python
from xai_finance.config import ROOT
from xai_finance.data.validate import validate_prices
from xai_finance.storage import read_json, sha256, write_json
```

يستورد ROOT وإجراء التحقق وعمليات JSON وSHA-256 الداخلية. تُستخدم للقراءة والكتابة والتحقق من اللقطات.

## الأسطر 13–17

```python
def yahoo_prices(specification: dict) -> tuple[pd.DataFrame, dict]:
    yf.set_tz_cache_location(str(ROOT / "data/provider_cache"))
    prices = yf.download(specification["symbol"], start=specification["start"], end=specification["end"], auto_adjust=False, actions=False, progress=False, threads=False, multi_level_index=False, timeout=30)
    if prices.empty:
        raise RuntimeError(f"Yahoo returned no genuine data for {specification['symbol']}; no synthetic fallback")
```

yahoo_prices تضبط مجلد ذاكرة المنطقة الزمنية وتطلب symbol والفترة من yfinance دون تعديل تلقائي أو أحداث، وبمهلة 30 ثانية وخيط تنزيل معطل. تعيد خطأ عند نتيجة فارغة بدلاً من اختلاق بيانات. الطلب شبكة فعلية عند استدعاء التنزيل.

## الأسطر 18–20

```python
    prices = prices.rename(columns=lambda column: column.lower().replace(" ", "_"))
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None).normalize()
    return prices, {"source_url": f"https://finance.yahoo.com/quote/{specification['symbol']}/history/", "timezone": "America/New_York exchange session date", "adjustment": "Yahoo Adj Close; OHLC multiplied by Adj Close/Close during feature extraction; volume unadjusted", "license": "Yahoo personal/research use; redistribution subject to Yahoo terms", "revision_caution": "Retrospectively adjusted snapshot, not point-in-time corporate-action vintages; continuous futures roll conventions provider-defined"}
```

توحد أسماء الأعمدة بأحرف صغيرة وشرطات سفلية، وتجرد فهرس الزمن من المنطقة الزمنية وتطبعه إلى اليوم، ثم تعيد الجدول وقاموس المصدر والوحدات الزمنية والتحفظ على التعديلات التاريخية. تطبيع اليوم ليس تحققاً من تاريخ الإتاحة.

## الأسطر 23–28

```python
def fred_prices(specification: dict) -> tuple[pd.DataFrame, dict]:
    url = f"https://fred.stlouisfed.org/graph/?g=0&id={specification['symbol']}&cosd={specification['start']}&coed={specification['end']}"
    csv_url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={specification['symbol']}"
    response = requests.get(csv_url, timeout=45)
    response.raise_for_status()
    prices = pd.read_csv(StringIO(response.text), index_col=0, parse_dates=True, na_values=".")
```

fred_prices تبني رابط وصف ورابط CSV للسلسلة، تطلب الثاني بمهلة 45 ثانية وتستدعي raise_for_status، ثم تقرأ النص بعمود تاريخ وتتعامل مع النقطة كقيمة ناقصة. أخطاء الشبكة أو HTTP تنتشر.

## الأسطر 29–31

```python
    prices.columns = ["close"]
    prices = prices.loc[(prices.index >= specification["start"]) & (prices.index < specification["end"])]
    return prices, {"source_url": url, "download_url": csv_url, "timezone": "monthly observation period", "adjustment": "Latest revised non-seasonally-adjusted index; no OHLCV invented", "license": "S&P Dow Jones Indices copyright; FRED series notes/terms apply", "revision_caution": "Exploratory retrospective next-observation experiment, NOT a real-time publication-date forecast. Release vintages and availability dates absent."}
```

تسمي عمود السلسلة close وتقتطع المدة start شاملة وend مستبعدة وتعيدها مع مصدر وترخيص وتنبيه البيانات المنقحة وعدم توافر تواريخ الإصدارات. تفترض أن CSV يحوي عمود قيمة واحداً.

## الأسطر 34–39

```python
def download_asset(asset: str, specification: dict) -> None:
    csv_path = ROOT / f"data/raw/{asset}.csv"
    if csv_path.exists():
        load_snapshot(asset)
        print(f"{asset}: verified existing snapshot", flush=True)
        return
```

download_asset تحدد مسار CSV؛ إذا وجد تستدعي load_snapshot للتحقق ثم تطبع وتعود، فلا تستبدله تلقائياً. وجود CSV دون manifest صالح يسبب خطأ بدلاً من تنزيل جديد.

## الأسطر 40–44

```python
    downloader = {"yahoo": yahoo_prices, "fred": fred_prices}[specification["provider"]]
    prices, provenance = downloader(specification)
    before = len(prices)
    prices = prices.apply(pd.to_numeric, errors="coerce").dropna()
    validate_prices(prices, specification["frequency"])
```

تختار دالة المزود حسب specification وتحمّل البيانات، تحفظ العدد الأولي، تحول القيم رقمياً مع تحويل غير الصالح إلى نقص ثم تحذف الصفوف الناقصة وتتحقق من الأسعار. مزود غير معروف يسبب KeyError.

## الأسطر 45–49

```python
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(csv_path, index_label="date", float_format="%.12g")
    manifest = {**specification, **provenance, "asset": asset, "status": "AUTHENTIC_PROVIDER_SNAPSHOT", "retrieved_utc": datetime.now(timezone.utc).isoformat(), "sha256": sha256(csv_path), "rows": len(prices), "rows_dropped_missing": before - len(prices), "first_date": str(prices.index.min().date()), "last_date": str(prices.index.max().date()), "max_calendar_gap_days": int(prices.index.to_series().diff().dt.days.max()), "negative_close_count": int((prices.close < 0).sum())}
    write_json(ROOT / f"data/manifests/{asset}.json", manifest)
    print(f"{asset}: saved {len(prices)} observations, sha256={manifest['sha256']}", flush=True)
```

تنشئ مجلد البيانات وتكتب CSV بدقة تنسيق 12 رقماً مع فهرس date، ثم تبني manifest يتضمن مواصفات المصدر والوقت والهاش والعدد والصفوف المحذوفة والمدى وأكبر فجوة وعدد الإغلاقات السالبة، وتكتب JSON وتطبع النتيجة. هذه آثار كتابة عند تشغيل التنزيل، ولم تنفذ في هذا التوثيق.

## الأسطر 52–56

```python
def load_snapshot(asset: str) -> tuple[pd.DataFrame, dict]:
    csv_path = ROOT / f"data/raw/{asset}.csv"
    manifest = read_json(ROOT / f"data/manifests/{asset}.json")
    if sha256(csv_path) != manifest["sha256"]:
        raise ValueError(f"Snapshot hash mismatch: {asset}")
```

load_snapshot تبني مسار اللقطة وتقرأ manifest وتقارن SHA-256 قبل قراءة الجدول؛ اختلاف البصمة يرفع ValueError. الهاش يكشف اختلاف البايتات عن القيمة المسجلة ولا يثبت وحده مصدر المزود.

## الأسطر 57–61

```python
    prices = pd.read_csv(csv_path, index_col="date", parse_dates=True)
    validate_prices(prices, manifest["frequency"])
    if len(prices) != manifest["rows"]:
        raise ValueError("Snapshot observation count mismatch")
    return prices, manifest
```

تقرأ CSV مع تاريخ فهرس وتطبق validate_prices وتقارن العدد المسجل قبل إرجاع الجدول والبيانات الوصفية. تعتمد التدريبات على هذا المسار؛ قد تنتشر أخطاء الملف أو parsing.

## الأسطر 64–66

```python
def download_all(configuration: dict) -> None:
    for asset in configuration["assets"]:
        download_asset(asset, configuration["datasets"][asset])
```

download_all تمر على الأصول المحددة في configuration وتستدعي download_asset مع إعداد كل أصل؛ لا تعيد قيمة. استخدام اللقطات الموجودة يمر بالتحقق بدلاً من الكتابة.
