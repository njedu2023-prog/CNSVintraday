from __future__ import annotations

import pandas as pd

from cnsvintraday.features.common import safe_divide


def build_vwap_features(frame: pd.DataFrame) -> dict[str, float]:
    amount = frame["amount"].fillna(0)
    volume = frame["volume"].fillna(0)
    cumulative_vwap = safe_divide(amount.sum(), volume.sum())
    close = frame["close"].iloc[-1]

    first_half = frame.head(max(len(frame) // 2, 1))
    second_half = frame.tail(max(len(frame) // 2, 1))
    vwap_first = safe_divide(first_half["amount"].sum(), first_half["volume"].sum())
    vwap_second = safe_divide(second_half["amount"].sum(), second_half["volume"].sum())

    return {
        "vwap": cumulative_vwap,
        "distance_to_vwap": safe_divide(close, cumulative_vwap) - 1.0,
        "price_above_vwap": 1.0 if close >= cumulative_vwap else 0.0,
        "vwap_trend": safe_divide(vwap_second, vwap_first) - 1.0,
    }
