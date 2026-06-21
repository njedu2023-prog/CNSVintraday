from __future__ import annotations

from datetime import time
from typing import Iterable

import pandas as pd

from cnsvintraday.core.context import IntradayContext


FUTURE_GUARD_VERSION = "1.1.1"
FUTURE_FIELD_BLACKLIST = (
    "next_trade_date",
    "t1",
    "t+1",
    "future",
    "label",
    "truth",
    "actual",
    "realized",
    "return_next",
    "next_close",
    "next_open",
    "next_high",
    "next_low",
)


def _series_times(values: Iterable[object]) -> list[time]:
    parsed = pd.to_datetime(pd.Series(list(values)), errors="coerce")
    return [value.time() for value in parsed.dropna().tolist()]


def check_no_future_columns(columns: Iterable[str]) -> list[str]:
    violations = []
    for column in columns:
        lower = column.lower()
        if any(keyword in lower for keyword in FUTURE_FIELD_BLACKLIST):
            violations.append(f"future/label column is not allowed in context: {column}")
    return violations


def check_minute_frame(frame: pd.DataFrame, cutoff: str = "14:00") -> list[str]:
    violations: list[str] = []
    violations.extend(check_no_future_columns(frame.columns))

    time_column = None
    for candidate in ("trade_time", "datetime", "timestamp", "feature_time"):
        if candidate in frame.columns:
            time_column = candidate
            break
    if time_column is None:
        return violations

    cutoff_time = pd.to_datetime(cutoff).time()
    for observed in _series_times(frame[time_column]):
        if observed > cutoff_time:
            violations.append(f"{time_column} contains data after cutoff {cutoff}: {observed}")
            break
    return violations


def apply_future_guard(context: IntradayContext, frames: list[pd.DataFrame] | None = None) -> IntradayContext:
    frames = frames or []
    violations: list[str] = []
    for frame in frames:
        violations.extend(check_minute_frame(frame, context.data_cutoff_time))
    if violations:
        for violation in violations:
            context.fail(violation)
    else:
        context.future_guard_passed = True
    context.future_guard_version = FUTURE_GUARD_VERSION
    context.formal_signal_allowed = False
    return context
