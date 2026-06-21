from __future__ import annotations

import pandas as pd

from cnsvintraday.features.common import safe_divide


def _tail_sum(series: pd.Series, window: int) -> float:
    return float(series.tail(window).sum())


def build_volume_features(frame: pd.DataFrame) -> dict[str, float]:
    volume = frame["volume"].fillna(0)
    amount = frame["amount"].fillna(0)
    avg_1m = safe_divide(volume.sum(), len(volume))
    volume_5m = _tail_sum(volume, 5)
    volume_15m = _tail_sum(volume, 15)
    volume_30m = _tail_sum(volume, 30)
    prev_5m = float(volume.tail(10).head(5).sum()) if len(volume) >= 10 else 0.0

    return {
        "volume_1m": float(volume.iloc[-1]),
        "volume_5m": volume_5m,
        "volume_15m": volume_15m,
        "volume_ratio_5m": safe_divide(volume_5m, avg_1m * 5),
        "volume_ratio_15m": safe_divide(volume_15m, avg_1m * 15),
        "volume_ratio_30m": safe_divide(volume_30m, avg_1m * 30),
        "volume_acceleration": safe_divide(volume_5m - prev_5m, max(prev_5m, 1.0)),
        "turnover_ratio": safe_divide(amount.sum(), max(frame["close"].iloc[-1] * volume.sum(), 1.0)),
    }
