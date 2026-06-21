from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

from cnsvintraday.validation.future_guard import check_no_future_columns


def check_feature_quality(frame: pd.DataFrame) -> dict[str, Any]:
    duplicate_columns = frame.columns[frame.columns.duplicated()].tolist()
    feature_columns = [c for c in frame.columns if c not in {"trade_date", "snapshot_time", "ts_code"}]
    missing_rates = {column: float(frame[column].isna().mean()) for column in feature_columns}
    nan_columns = [column for column, rate in missing_rates.items() if rate > 0]
    inf_columns = []
    constant_columns = []

    for column in feature_columns:
        series = pd.to_numeric(frame[column], errors="coerce")
        if series.map(lambda value: isinstance(value, float) and math.isinf(value)).any():
            inf_columns.append(column)
        if len(frame) > 1 and series.nunique(dropna=True) <= 1:
            constant_columns.append(column)

    future_violations = check_no_future_columns(frame.columns)
    status = "PASS"
    if duplicate_columns or inf_columns or future_violations:
        status = "FAIL"
    elif nan_columns or constant_columns:
        status = "WARN"

    return {
        "status": status,
        "feature_count": len(feature_columns),
        "missing_rates": missing_rates,
        "nan_columns": nan_columns,
        "inf_columns": inf_columns,
        "duplicate_columns": duplicate_columns,
        "constant_columns": constant_columns,
        "future_violations": future_violations,
    }


def write_feature_quality(frame: pd.DataFrame, path: Path) -> dict[str, Any]:
    quality = check_feature_quality(frame)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return quality
