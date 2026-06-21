from __future__ import annotations

from typing import Any

import pandas as pd

from cnsvintraday.decision.decision_loader import DecisionInputs
from cnsvintraday.validation.future_guard import FUTURE_FIELD_BLACKLIST


ALLOWED_FUTURE_COLUMNS = {"next_trade_date"}


def future_column_violations(frame: pd.DataFrame | None, name: str) -> list[str]:
    if frame is None:
        return []
    violations = []
    for column in frame.columns:
        if column in ALLOWED_FUTURE_COLUMNS:
            continue
        lower = column.lower()
        if any(keyword in lower for keyword in FUTURE_FIELD_BLACKLIST):
            violations.append(f"{name} contains future field: {column}")
    return violations


def _context_value(context: dict[str, Any] | None, key: str, default: Any = None) -> Any:
    if not context:
        return default
    return context.get(key, default)


def evaluate_decision_gate(inputs: DecisionInputs) -> dict[str, Any]:
    warnings = list(inputs.warning_messages)
    failures = list(inputs.fail_reasons)
    context = inputs.context or {}
    learning_state = inputs.learning_state or {}

    if _context_value(context, "ready", False) is False:
        failures.append("context.ready=false")
    if str(_context_value(context, "status", "FAIL")).upper() == "FAIL":
        failures.append("context.status=FAIL")
    elif str(_context_value(context, "status", "")).upper() == "WARN":
        warnings.append("context.status=WARN")
    if _context_value(context, "future_guard_passed", False) is False:
        failures.append("context.future_guard_passed=false")
    if _context_value(context, "formal_signal_allowed", False) is True:
        failures.append("formal_signal_allowed=true")
    if learning_state.get("allowed_usage", {}).get("can_generate_formal_signal") is True:
        failures.append("can_generate_formal_signal=true")

    failures.extend(future_column_violations(inputs.feature_snapshot, "feature_snapshot"))
    failures.extend(future_column_violations(inputs.prediction_snapshot, "prediction_snapshot"))
    failures.extend(future_column_violations(inputs.path_distribution, "path_distribution"))

    if inputs.prediction_snapshot is not None and inputs.path_distribution is not None and context:
        trade_date = str(context.get("trade_date", ""))
        next_trade_date = str(context.get("next_trade_date", ""))
        for name, frame in (("prediction_snapshot", inputs.prediction_snapshot), ("path_distribution", inputs.path_distribution)):
            if not frame.empty:
                latest = frame.tail(1).iloc[0]
                if str(latest.get("trade_date", "")) != trade_date or str(latest.get("next_trade_date", "")) != next_trade_date:
                    failures.append(f"{name} trade_date/next_trade_date mismatch")

    if inputs.learning_state is None:
        warnings.append("Learning State Missing")
    else:
        if inputs.learning_state.get("sample_count", 0) < 20:
            warnings.append("learning sample_count insufficient")
        if inputs.learning_state.get("drift_status") == "DEGRADING":
            warnings.append("drift_status=DEGRADING")
        if inputs.learning_state.get("calibration_status") == "INSUFFICIENT":
            warnings.append("calibration_status=INSUFFICIENT")

    if inputs.learning_metrics is None:
        warnings.append("Learning Metrics Missing")
    if inputs.feature_quality is None:
        warnings.append("Feature Quality Missing")
    if inputs.model_leaderboard is None:
        warnings.append("Model Leaderboard Missing")
    if inputs.path_metrics is None:
        warnings.append("Path Metrics Missing")

    status = "FAIL" if failures else ("WARN" if warnings else "PASS")
    return {
        "report_status": status,
        "observation_allowed": status in {"PASS", "WARN"},
        "formal_signal_allowed": False,
        "warning_messages": sorted(set(warnings)),
        "fail_reasons": sorted(set(failures)),
    }
