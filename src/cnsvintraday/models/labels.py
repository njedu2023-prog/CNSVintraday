from __future__ import annotations

import pandas as pd

from cnsvintraday.features.common import safe_divide


REQUIRED_LABEL_SOURCE_COLUMNS = {"trade_date", "next_trade_date", "price_1400", "next_close"}


def build_t1_labels(frame: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(REQUIRED_LABEL_SOURCE_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"label source missing required columns: {missing}")

    work = frame.copy()
    work["price_1400"] = pd.to_numeric(work["price_1400"], errors="coerce")
    work["next_close"] = pd.to_numeric(work["next_close"], errors="coerce")
    if work[["price_1400", "next_close"]].isna().any().any():
        raise ValueError("label source contains invalid price values")

    return pd.DataFrame(
        {
            "trade_date": work["trade_date"].astype(str),
            "next_trade_date": work["next_trade_date"].astype(str),
            "label_up_t1": (work["next_close"] > work["price_1400"]).astype(int),
            "label_return_t1": [
                safe_divide(next_close, price) - 1.0
                for price, next_close in zip(work["price_1400"], work["next_close"], strict=True)
            ],
        }
    )
