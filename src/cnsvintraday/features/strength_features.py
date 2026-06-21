from __future__ import annotations

import pandas as pd

from cnsvintraday.features.common import safe_divide


def build_strength_features(frame: pd.DataFrame) -> dict[str, float]:
    high = frame["high"]
    low = frame["low"]
    close = frame["close"]
    last_close = close.iloc[-1]
    prior_high = high.iloc[:-1].max() if len(high) > 1 else high.iloc[-1]
    prior_low = low.iloc[:-1].min() if len(low) > 1 else low.iloc[-1]
    intraday_high = high.max()
    intraday_low = low.min()
    day_range = intraday_high - intraday_low
    close_strength = safe_divide(last_close - intraday_low, day_range)
    open_to_close = safe_divide(last_close, frame["open"].iloc[0]) - 1.0

    return {
        "high_break": 1.0 if last_close > prior_high else 0.0,
        "low_break": 1.0 if last_close < prior_low else 0.0,
        "new_high_intraday": 1.0 if high.iloc[-1] >= intraday_high else 0.0,
        "new_low_intraday": 1.0 if low.iloc[-1] <= intraday_low else 0.0,
        "close_strength": close_strength,
        "intraday_strength_score": (close_strength + max(min(open_to_close * 10.0, 1.0), -1.0)) / 2.0,
    }
