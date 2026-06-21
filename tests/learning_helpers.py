from __future__ import annotations

import pandas as pd


def make_prediction_frame(days: int = 160, models: tuple[str, ...] = ("B0", "B1")) -> pd.DataFrame:
    records = []
    for day in range(days):
        trade_date = f"2026{day + 1:04d}"
        next_trade_date = f"2026{day + 2:04d}"
        actual_up = 1 if day % 2 == 0 else 0
        for model_index, model_name in enumerate(models):
            prob_up = 0.72 if actual_up else 0.28
            if model_index == 1:
                prob_up = 0.62 if actual_up else 0.38
            records.append(
                {
                    "trade_date": trade_date,
                    "next_trade_date": next_trade_date,
                    "model_name": model_name,
                    "prob_up": prob_up,
                    "prob_down": 1.0 - prob_up,
                    "expected_return": 0.01 if actual_up else -0.01,
                    "confidence": abs(prob_up - 0.5) * 2.0,
                }
            )
    return pd.DataFrame(records)


def make_path_frame(days: int = 160) -> pd.DataFrame:
    records = []
    for day in range(days):
        records.append(
            {
                "trade_date": f"2026{day + 1:04d}",
                "next_trade_date": f"2026{day + 2:04d}",
                "path_p10": -0.03,
                "path_p25": -0.01,
                "path_p50": 0.0,
                "path_p75": 0.01,
                "path_p90": 0.03,
                "price_p10": 97.0,
                "price_p25": 99.0,
                "price_p50": 100.0,
                "price_p75": 101.0,
                "price_p90": 103.0,
                "downside_risk": -0.03,
                "upside_potential": 0.03,
                "expected_range": 0.06,
            }
        )
    return pd.DataFrame(records)


def make_truth_frame(days: int = 160) -> pd.DataFrame:
    records = []
    for day in range(days):
        actual_return = 0.012 if day % 2 == 0 else -0.012
        records.append(
            {
                "trade_date": f"2026{day + 1:04d}",
                "next_trade_date": f"2026{day + 2:04d}",
                "close_1400": 100.0,
                "next_open": 100.5,
                "next_high": 103.0,
                "next_low": 97.0,
                "next_close": 100.0 * (1.0 + actual_return),
                "actual_return_t1": actual_return,
                "actual_up_t1": 1 if actual_return > 0 else 0,
            }
        )
    return pd.DataFrame(records)

