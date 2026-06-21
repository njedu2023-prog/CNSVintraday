from __future__ import annotations

import pandas as pd

from cnsvintraday.features.common import slope


def _ma(close: pd.Series, window: int) -> float:
    return float(close.tail(window).mean())


def build_trend_features(frame: pd.DataFrame) -> dict[str, float]:
    close = frame["close"]
    last_close = close.iloc[-1]
    ma5 = _ma(close, 5)
    ma10 = _ma(close, 10)
    ma20 = _ma(close, 20)

    return {
        "ma5": ma5,
        "ma10": ma10,
        "ma20": ma20,
        "price_above_ma5": 1.0 if last_close >= ma5 else 0.0,
        "price_above_ma10": 1.0 if last_close >= ma10 else 0.0,
        "price_above_ma20": 1.0 if last_close >= ma20 else 0.0,
        "ma5_slope": slope(close.rolling(5, min_periods=1).mean(), 5),
        "ma10_slope": slope(close.rolling(10, min_periods=1).mean(), 10),
        "ma20_slope": slope(close.rolling(20, min_periods=1).mean(), 20),
    }
