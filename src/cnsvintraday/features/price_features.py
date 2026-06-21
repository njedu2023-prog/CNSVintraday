from __future__ import annotations

import pandas as pd

from cnsvintraday.features.common import safe_divide, trailing_return


def build_price_features(frame: pd.DataFrame) -> dict[str, float]:
    close = frame["close"]
    open_first = frame["open"].iloc[0]
    high = frame["high"].max()
    low = frame["low"].min()
    last_close = close.iloc[-1]
    day_range = high - low

    return {
        "return_1m": trailing_return(close, 1),
        "return_5m": trailing_return(close, 5),
        "return_15m": trailing_return(close, 15),
        "return_30m": trailing_return(close, 30),
        "return_60m": trailing_return(close, 60),
        "high_to_close": safe_divide(last_close, high) - 1.0,
        "low_to_close": safe_divide(last_close, low) - 1.0,
        "open_to_close": safe_divide(last_close, open_first) - 1.0,
        "day_range_pct": safe_divide(day_range, open_first),
        "close_position": min(max(safe_divide(last_close - low, day_range), 0.0), 1.0),
    }
