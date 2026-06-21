from __future__ import annotations

import math

import pandas as pd


def prepare_minute_frame(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"trade_date", "ts_code", "trade_time", "open", "high", "low", "close", "volume"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"minute frame missing required columns: {missing}")

    work = frame.copy()
    work["trade_time"] = pd.to_datetime(work["trade_time"], errors="coerce")
    if work["trade_time"].isna().any():
        raise ValueError("minute frame contains unparseable trade_time")

    for column in ("open", "high", "low", "close", "volume", "amount"):
        if column in work.columns:
            work[column] = pd.to_numeric(work[column], errors="coerce")

    if "amount" not in work.columns:
        work["amount"] = work["close"] * work["volume"]

    return work.sort_values("trade_time").reset_index(drop=True)


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator is None or denominator == 0 or pd.isna(denominator):
        return 0.0
    value = numerator / denominator
    if math.isinf(value) or math.isnan(value):
        return 0.0
    return float(value)


def trailing_return(close: pd.Series, window: int) -> float:
    if len(close) <= window:
        first = close.iloc[0]
    else:
        first = close.iloc[-window - 1]
    last = close.iloc[-1]
    return safe_divide(last, first) - 1.0


def slope(values: pd.Series, window: int) -> float:
    tail = values.tail(window)
    if len(tail) < 2:
        return 0.0
    return safe_divide(tail.iloc[-1] - tail.iloc[0], max(abs(tail.iloc[0]), 1e-12))
