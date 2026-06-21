from __future__ import annotations

from pathlib import Path

import pandas as pd


TRUTH_COLUMN_ALIASES = {
    "close_1400": ("close_1400", "price_1400"),
    "next_close": ("next_close", "close_t1"),
    "next_open": ("next_open", "open_t1"),
    "next_high": ("next_high", "high_t1"),
    "next_low": ("next_low", "low_t1"),
    "actual_return_t1": ("actual_return_t1", "label_return_t1", "return_t1"),
    "actual_up_t1": ("actual_up_t1", "label_up_t1", "up_t1"),
}

TRUTH_REQUIRED_COLUMNS = {"trade_date", "next_trade_date", "actual_return_t1", "actual_up_t1", "next_close"}


def normalize_truth_frame(truth: pd.DataFrame) -> pd.DataFrame:
    normalized = truth.copy()
    for canonical, aliases in TRUTH_COLUMN_ALIASES.items():
        if canonical in normalized.columns:
            continue
        for alias in aliases:
            if alias in normalized.columns:
                normalized[canonical] = normalized[alias]
                break
    missing = sorted(TRUTH_REQUIRED_COLUMNS - set(normalized.columns))
    if missing:
        raise ValueError(f"truth frame missing required columns: {missing}")
    normalized["trade_date"] = normalized["trade_date"].astype(str)
    normalized["next_trade_date"] = normalized["next_trade_date"].astype(str)
    return normalized


def join_prediction_truth(prediction_log: pd.DataFrame, truth: pd.DataFrame | None = None) -> pd.DataFrame:
    base = prediction_log.copy()
    base["trade_date"] = base["trade_date"].astype(str)
    base["next_trade_date"] = base["next_trade_date"].astype(str)
    truth_columns = ["actual_return_t1", "actual_up_t1", "next_close"]
    if truth is None or truth.empty:
        joined = base.copy()
        for column in truth_columns:
            joined[column] = pd.NA
        joined["joined_status"] = "PENDING_TRUTH"
        return joined

    normalized = normalize_truth_frame(truth)
    keep = ["trade_date", "next_trade_date", *truth_columns]
    joined = base.merge(normalized[keep], on=["trade_date", "next_trade_date"], how="left")
    missing_truth = joined[truth_columns].isna().any(axis=1)
    joined["joined_status"] = "JOINED"
    joined.loc[missing_truth, "joined_status"] = "PENDING_TRUTH"
    return joined


def write_prediction_truth_joined(data_root: Path, joined: pd.DataFrame) -> Path:
    path = data_root / "data" / "learning" / "prediction_truth_joined_latest.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    joined.to_parquet(path, index=False)
    return path

