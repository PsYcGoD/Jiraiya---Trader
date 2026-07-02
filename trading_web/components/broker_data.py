import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv:
    load_dotenv()


@dataclass
class DataResult:
    frame: pd.DataFrame
    source: str
    message: str


def clean_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    rename = {
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    }
    df = df.rename(columns={c: rename.get(str(c).lower(), c) for c in df.columns})
    keep = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    df = df[keep]
    for col in ["Open", "High", "Low", "Close"]:
        if col in df:
            df = df[pd.to_numeric(df[col], errors="coerce") > 0]
    return df.dropna()


def fetch_market_data(
    source: str,
    symbol: str,
    mode: str,
    interval: str,
    lookback_days: int,
    daily_period: str,
) -> DataResult:
    source_key = str(source or "Yahoo").lower()
    if source_key.startswith("kite"):
        return fetch_kite(symbol, mode, interval, lookback_days, daily_period)
    if source_key.startswith("dhan"):
        return fetch_dhan(symbol, mode, interval, lookback_days, daily_period)
    return fetch_yahoo(symbol, mode, interval, lookback_days, daily_period)


def fetch_yahoo(symbol: str, mode: str, interval: str, lookback_days: int, daily_period: str) -> DataResult:
    if mode == "Intraday":
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(days=int(lookback_days or 5))
        df = yf.Ticker(symbol).history(
            start=start_dt,
            end=end_dt,
            interval=interval,
            auto_adjust=False,
            actions=False,
        )
        msg = f"Yahoo Finance intraday {interval}, last {lookback_days} day(s)"
    else:
        df = yf.Ticker(symbol).history(
            period=daily_period,
            interval="1d",
            auto_adjust=False,
            actions=False,
        )
        msg = f"Yahoo Finance daily {daily_period}"
    return DataResult(clean_ohlc(df), "Yahoo Finance", msg)


def fetch_kite(symbol: str, mode: str, interval: str, lookback_days: int, daily_period: str) -> DataResult:
    try:
        from kiteconnect import KiteConnect
    except Exception as exc:
        raise RuntimeError("KiteConnect is not installed. Run: pip install kiteconnect") from exc

    api_key = os.getenv("KITE_API_KEY")
    access_token = os.getenv("KITE_ACCESS_TOKEN")
    if not api_key or not access_token:
        raise RuntimeError("Missing KITE_API_KEY or KITE_ACCESS_TOKEN in environment.")

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    exchange = os.getenv("KITE_EXCHANGE", "NSE")
    token = _kite_find_instrument_token(kite, exchange, symbol)
    if token is None:
        raise RuntimeError(f"Could not find Kite instrument token for {exchange}:{symbol}.")

    end_dt = datetime.now()
    if mode == "Intraday":
        start_dt = end_dt - timedelta(days=int(lookback_days or 5))
        kite_interval = _kite_interval(interval)
    else:
        start_dt = end_dt - _period_to_timedelta(daily_period)
        kite_interval = "day"

    rows = kite.historical_data(token, start_dt, end_dt, kite_interval)
    df = pd.DataFrame(rows)
    if "date" in df:
        df = df.set_index("date")
    return DataResult(clean_ohlc(df), "Kite", f"Kite historical {kite_interval} for {exchange}:{symbol}")


def fetch_dhan(symbol: str, mode: str, interval: str, lookback_days: int, daily_period: str) -> DataResult:
    try:
        from dhanhq import DhanContext, dhanhq
    except Exception:
        try:
            from dhanhq import dhanhq
            DhanContext = None
        except Exception as exc:
            raise RuntimeError("dhanhq is not installed. Run: pip install dhanhq") from exc

    client_id = os.getenv("DHAN_CLIENT_ID")
    token = os.getenv("DHAN_TOKEN")
    if not client_id or not token:
        raise RuntimeError("Missing DHAN_CLIENT_ID or DHAN_TOKEN in environment.")

    client = dhanhq(DhanContext(client_id, token)) if DhanContext else dhanhq(client_id, token)
    security_id = _dhan_security_id_for(symbol)
    if not security_id:
        raise RuntimeError(
            "Dhan historical data needs a security id. Set DHAN_SECURITY_ID or "
            f"DHAN_SECURITY_ID_{_env_symbol(symbol)} in your environment."
        )

    exchange_segment = os.getenv("DHAN_EXCHANGE_SEGMENT", "NSE_EQ")
    end_dt = datetime.now()
    if mode == "Intraday":
        start_dt = end_dt - timedelta(days=int(lookback_days or 5))
        if not hasattr(client, "intraday_minute_data"):
            raise RuntimeError("Installed dhanhq client does not expose intraday_minute_data.")
        payload = client.intraday_minute_data(
            security_id=str(security_id),
            exchange_segment=exchange_segment,
            instrument_type=os.getenv("DHAN_INSTRUMENT_TYPE", "EQUITY"),
            from_date=start_dt.strftime("%Y-%m-%d"),
            to_date=end_dt.strftime("%Y-%m-%d"),
            interval=int(str(interval).replace("m", "") or 1),
        )
    else:
        start_dt = end_dt - _period_to_timedelta(daily_period)
        if not hasattr(client, "historical_daily_data"):
            raise RuntimeError("Installed dhanhq client does not expose historical_daily_data.")
        payload = client.historical_daily_data(
            security_id=str(security_id),
            exchange_segment=exchange_segment,
            instrument_type=os.getenv("DHAN_INSTRUMENT_TYPE", "EQUITY"),
            from_date=start_dt.strftime("%Y-%m-%d"),
            to_date=end_dt.strftime("%Y-%m-%d"),
        )

    rows = payload.get("data", payload) if isinstance(payload, dict) else payload
    df = pd.DataFrame(rows)
    for date_col in ["date", "start_Time", "start_time", "timestamp"]:
        if date_col in df:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df = df.set_index(date_col)
            break
    return DataResult(clean_ohlc(df), "Dhan", f"Dhan historical data for security_id={security_id}")


def credential_status() -> dict[str, str]:
    return {
        "Dhan": "ready" if os.getenv("DHAN_CLIENT_ID") and os.getenv("DHAN_TOKEN") else "missing env",
        "Kite": "ready" if os.getenv("KITE_API_KEY") and os.getenv("KITE_ACCESS_TOKEN") else "missing env",
    }


def _kite_find_instrument_token(kite, exchange: str, symbol: str) -> Optional[int]:
    rows = kite.instruments(exchange)
    target = str(symbol).upper().replace(".NS", "")
    for row in rows:
        trading_symbol = str(row.get("tradingsymbol", "")).upper()
        if trading_symbol == target:
            return int(row.get("instrument_token"))
    return None


def _kite_interval(interval: str) -> str:
    return {
        "1m": "minute",
        "2m": "2minute",
        "5m": "5minute",
        "15m": "15minute",
    }.get(interval, "5minute")


def _period_to_timedelta(period: str) -> timedelta:
    value = str(period or "6mo").lower()
    if value.endswith("mo"):
        return timedelta(days=30 * int(value[:-2] or 6))
    if value.endswith("y"):
        return timedelta(days=365 * int(value[:-1] or 1))
    if value.endswith("d"):
        return timedelta(days=int(value[:-1] or 30))
    return timedelta(days=180)


def _env_symbol(symbol: str) -> str:
    return str(symbol or "").upper().replace(".", "_").replace("-", "_")


def _dhan_security_id_for(symbol: str) -> Optional[str]:
    specific = os.getenv(f"DHAN_SECURITY_ID_{_env_symbol(symbol)}")
    return specific or os.getenv("DHAN_SECURITY_ID")
