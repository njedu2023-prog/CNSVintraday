from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from cnsvintraday.decision import DECISION_VERSION


def build_decision_summary(
    context: dict[str, Any] | None,
    gate: dict[str, Any],
    model_summary: dict[str, Any],
    path_summary: dict[str, Any],
    risk_summary: dict[str, Any],
    learning_summary: dict[str, Any],
    missing_files: list[str],
) -> dict[str, Any]:
    context = context or {}
    selected = model_summary.get("selected_prediction", {})
    returns = path_summary.get("returns", {})
    prices = path_summary.get("prices", {})
    summary = {
        "version": DECISION_VERSION,
        "trade_date": str(context.get("trade_date", path_summary.get("trade_date", ""))),
        "next_trade_date": str(context.get("next_trade_date", path_summary.get("next_trade_date", ""))),
        "snapshot_time": str(context.get("snapshot_time", "1400")),
        "report_status": gate["report_status"],
        "observation_allowed": bool(gate["observation_allowed"]),
        "formal_signal_allowed": False,
        "prediction": {
            "prob_up": selected.get("prob_up"),
            "prob_down": selected.get("prob_down"),
            "expected_return": selected.get("expected_return"),
            "confidence": selected.get("confidence"),
        },
        "path_distribution": {
            "path_p10": returns.get("path_p10"),
            "path_p50": returns.get("path_p50"),
            "path_p90": returns.get("path_p90"),
            "price_p10": prices.get("price_p10"),
            "price_p50": prices.get("price_p50"),
            "price_p90": prices.get("price_p90"),
        },
        "risk": risk_summary,
        "model_summary": model_summary,
        "learning_summary": learning_summary,
        "data_quality": {
            "ready": context.get("ready"),
            "status": context.get("status"),
            "future_guard_passed": context.get("future_guard_passed"),
        },
        "missing_files": missing_files,
        "warning_messages": gate["warning_messages"],
        "fail_reasons": gate["fail_reasons"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return summary
