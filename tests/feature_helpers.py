from __future__ import annotations

import pandas as pd


def make_minute_frame(rows: int = 61) -> pd.DataFrame:
    trade_times = pd.date_range("2026-06-22 09:30:00", periods=rows, freq="min")
    close = pd.Series([10.0 + index * 0.03 for index in range(rows)])
    volume = pd.Series([1000 + index * 20 for index in range(rows)])
    return pd.DataFrame(
        {
            "trade_date": ["20260622"] * rows,
            "ts_code": ["600150.SH"] * rows,
            "trade_time": trade_times,
            "open": close - 0.01,
            "high": close + 0.05,
            "low": close - 0.05,
            "close": close,
            "volume": volume,
            "amount": close * volume,
        }
    )
