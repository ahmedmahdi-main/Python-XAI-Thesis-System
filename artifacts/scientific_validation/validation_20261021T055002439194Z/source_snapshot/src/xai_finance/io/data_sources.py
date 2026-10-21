from datetime import datetime, timezone
from io import StringIO

import pandas as pd
import requests
import yfinance as yf

from xai_finance.config import ROOT
from xai_finance.data.validate import validate_prices
from xai_finance.storage import read_json, sha256, write_json


def yahoo_prices(specification: dict) -> tuple[pd.DataFrame, dict]:
    yf.set_tz_cache_location(str(ROOT / "data/provider_cache"))
    prices = yf.download(specification["symbol"], start=specification["start"], end=specification["end"], auto_adjust=False, actions=False, progress=False, threads=False, multi_level_index=False, timeout=30)
    if prices.empty:
        raise RuntimeError(f"Yahoo returned no genuine data for {specification['symbol']}; no synthetic fallback")
    prices = prices.rename(columns=lambda column: column.lower().replace(" ", "_"))
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None).normalize()
    return prices, {"source_url": f"https://finance.yahoo.com/quote/{specification['symbol']}/history/", "timezone": "America/New_York exchange session date", "adjustment": "Yahoo Adj Close; OHLC multiplied by Adj Close/Close during feature extraction; volume unadjusted", "license": "Yahoo personal/research use; redistribution subject to Yahoo terms", "revision_caution": "Retrospectively adjusted snapshot, not point-in-time corporate-action vintages; continuous futures roll conventions provider-defined"}


def fred_prices(specification: dict) -> tuple[pd.DataFrame, dict]:
    url = f"https://fred.stlouisfed.org/graph/?g=0&id={specification['symbol']}&cosd={specification['start']}&coed={specification['end']}"
    csv_url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={specification['symbol']}"
    response = requests.get(csv_url, timeout=45)
    response.raise_for_status()
    prices = pd.read_csv(StringIO(response.text), index_col=0, parse_dates=True, na_values=".")
    prices.columns = ["close"]
    prices = prices.loc[(prices.index >= specification["start"]) & (prices.index < specification["end"])]
    return prices, {"source_url": url, "download_url": csv_url, "timezone": "monthly observation period", "adjustment": "Latest revised non-seasonally-adjusted index; no OHLCV invented", "license": "S&P Dow Jones Indices copyright; FRED series notes/terms apply", "revision_caution": "Exploratory retrospective next-observation experiment, NOT a real-time publication-date forecast. Release vintages and availability dates absent."}


def download_asset(asset: str, specification: dict) -> None:
    csv_path = ROOT / f"data/raw/{asset}.csv"
    if csv_path.exists():
        load_snapshot(asset)
        print(f"{asset}: verified existing snapshot", flush=True)
        return
    downloader = {"yahoo": yahoo_prices, "fred": fred_prices}[specification["provider"]]
    prices, provenance = downloader(specification)
    before = len(prices)
    prices = prices.apply(pd.to_numeric, errors="coerce").dropna()
    validate_prices(prices, specification["frequency"])
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(csv_path, index_label="date", float_format="%.12g")
    manifest = {**specification, **provenance, "asset": asset, "status": "AUTHENTIC_PROVIDER_SNAPSHOT", "retrieved_utc": datetime.now(timezone.utc).isoformat(), "sha256": sha256(csv_path), "rows": len(prices), "rows_dropped_missing": before - len(prices), "first_date": str(prices.index.min().date()), "last_date": str(prices.index.max().date()), "max_calendar_gap_days": int(prices.index.to_series().diff().dt.days.max()), "negative_close_count": int((prices.close < 0).sum())}
    write_json(ROOT / f"data/manifests/{asset}.json", manifest)
    print(f"{asset}: saved {len(prices)} observations, sha256={manifest['sha256']}", flush=True)


def load_snapshot(asset: str) -> tuple[pd.DataFrame, dict]:
    csv_path = ROOT / f"data/raw/{asset}.csv"
    manifest = read_json(ROOT / f"data/manifests/{asset}.json")
    if sha256(csv_path) != manifest["sha256"]:
        raise ValueError(f"Snapshot hash mismatch: {asset}")
    prices = pd.read_csv(csv_path, index_col="date", parse_dates=True)
    validate_prices(prices, manifest["frequency"])
    if len(prices) != manifest["rows"]:
        raise ValueError("Snapshot observation count mismatch")
    return prices, manifest


def download_all(configuration: dict) -> None:
    for asset in configuration["assets"]:
        download_asset(asset, configuration["datasets"][asset])
