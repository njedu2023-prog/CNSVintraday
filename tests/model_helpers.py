from __future__ import annotations

import pandas as pd

from cnsvintraday.features.feature_manifest import feature_names


def make_feature_frame(rows: int = 151) -> pd.DataFrame:
    records = []
    names = feature_names()
    for index in range(rows):
        trend = (index % 20 - 10) / 1000
        row = {
            "trade_date": f"2026{index + 1:04d}",
            "snapshot_time": "1400",
            "ts_code": "600150.SH",
        }
        for feature in names:
            row[feature] = trend
        row["return_15m"] = trend
        row["return_30m"] = trend * 1.2
        row["return_60m"] = trend * 1.5
        row["distance_to_vwap"] = -trend
        row["close_position"] = max(min(0.5 + trend * 10, 1.0), 0.0)
        records.append(row)
    return pd.DataFrame(records)


def make_label_source(rows: int = 151) -> pd.DataFrame:
    records = []
    for index in range(rows):
        trade_date = f"2026{index + 1:04d}"
        base = 10.0
        next_close = base * (1.0 + ((index % 20 - 10) / 1000))
        records.append(
            {
                "trade_date": trade_date,
                "next_trade_date": f"2026{index + 2:04d}",
                "price_1400": base,
                "next_close": next_close,
            }
        )
    return pd.DataFrame(records)
