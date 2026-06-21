from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from cnsvintraday.features import FEATURE_VERSION
from cnsvintraday.models import BASELINE_MODEL_VERSION
from cnsvintraday.paths import PATH_DISTRIBUTION_VERSION


PREDICTION_REQUIRED_COLUMNS = {
    "trade_date",
    "next_trade_date",
    "model_name",
    "prob_up",
    "prob_down",
    "expected_return",
    "confidence",
}

PATH_REQUIRED_COLUMNS = {
    "trade_date",
    "next_trade_date",
    "path_p10",
    "path_p25",
    "path_p50",
    "path_p75",
    "path_p90",
    "price_p10",
    "price_p25",
    "price_p50",
    "price_p75",
    "price_p90",
}


def prediction_log_paths(data_root: Path, trade_date: str, snapshot_time: str = "1400") -> dict[str, Path]:
    return {
        "latest": data_root / "data" / "learning" / "prediction_log_latest.parquet",
        "history": data_root / "data" / "learning" / "history" / f"prediction_log_{trade_date}_{snapshot_time}.parquet",
    }


def _require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def build_prediction_log(
    predictions: pd.DataFrame,
    paths: pd.DataFrame,
    snapshot_time: str = "1400",
    created_at: str | None = None,
) -> pd.DataFrame:
    _require_columns(predictions, PREDICTION_REQUIRED_COLUMNS, "prediction snapshot")
    _require_columns(paths, PATH_REQUIRED_COLUMNS, "path distribution")

    work = predictions.copy()
    path_cols = [column for column in paths.columns if column not in {"path_version"}]
    merged = work.merge(paths[path_cols], on=["trade_date", "next_trade_date"], how="left")
    path_missing = merged[["path_p10", "path_p50", "path_p90"]].isna().any(axis=1)
    if path_missing.any():
        raise ValueError("prediction log missing path distribution for one or more predictions")

    trade_dates = merged["trade_date"].astype(str)
    run_id_date = str(trade_dates.max())
    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    merged.insert(0, "run_id", f"{run_id_date}_{snapshot_time}")
    merged["trade_date"] = trade_dates
    merged["next_trade_date"] = merged["next_trade_date"].astype(str)
    merged["snapshot_time"] = merged.get("snapshot_time", snapshot_time)
    merged["model_version"] = merged.get("model_version", BASELINE_MODEL_VERSION)
    merged["feature_version"] = merged.get("feature_version", FEATURE_VERSION)
    merged["path_version"] = merged.get("path_version", PATH_DISTRIBUTION_VERSION)
    merged["created_at"] = timestamp
    merged["formal_signal_allowed"] = False
    return merged[
        [
            "run_id",
            "trade_date",
            "next_trade_date",
            "snapshot_time",
            "model_name",
            "model_version",
            "feature_version",
            "path_version",
            "prob_up",
            "prob_down",
            "expected_return",
            "confidence",
            "path_p10",
            "path_p25",
            "path_p50",
            "path_p75",
            "path_p90",
            "price_p10",
            "price_p25",
            "price_p50",
            "price_p75",
            "price_p90",
            "created_at",
            "formal_signal_allowed",
        ]
    ]


def write_prediction_log(data_root: Path, log: pd.DataFrame, snapshot_time: str = "1400") -> dict[str, Path]:
    trade_date = str(log["trade_date"].max())
    paths = prediction_log_paths(data_root, trade_date, snapshot_time=snapshot_time)
    for output_path in paths.values():
        output_path.parent.mkdir(parents=True, exist_ok=True)
        log.to_parquet(output_path, index=False)
    return paths

