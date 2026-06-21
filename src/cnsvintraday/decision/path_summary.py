from __future__ import annotations

from typing import Any

import pandas as pd


PATH_COLUMNS = ("path_p10", "path_p25", "path_p50", "path_p75", "path_p90")
PRICE_COLUMNS = ("price_p10", "price_p25", "price_p50", "price_p75", "price_p90")


def build_path_summary(paths: pd.DataFrame | None) -> dict[str, Any]:
    if paths is None or paths.empty:
        return {"available": False}
    row = paths.tail(1).iloc[0]
    return {
        "available": True,
        "trade_date": str(row.get("trade_date", "")),
        "next_trade_date": str(row.get("next_trade_date", "")),
        "returns": {column: float(row[column]) for column in PATH_COLUMNS if column in row},
        "prices": {column: float(row[column]) for column in PRICE_COLUMNS if column in row},
        "expected_range": float(row.get("expected_range", row.get("path_p90", 0.0) - row.get("path_p10", 0.0))),
        "downside_risk": float(row.get("downside_risk", row.get("path_p10", 0.0))),
        "upside_potential": float(row.get("upside_potential", row.get("path_p90", 0.0))),
        "notes": [
            "P10 is a pessimistic scenario.",
            "P50 is the median scenario.",
            "P90 is an optimistic scenario, not a guaranteed target.",
        ],
    }
