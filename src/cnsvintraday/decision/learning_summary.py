from __future__ import annotations

from typing import Any


def _window(metrics: dict[str, Any] | None, name: str) -> dict[str, Any]:
    if not metrics:
        return {"sample_status": "MISSING"}
    return metrics.get("windows", {}).get(name, {}).get("overall", {"sample_status": "MISSING"})


def build_learning_summary(state: dict[str, Any] | None, metrics: dict[str, Any] | None) -> dict[str, Any]:
    if state is None:
        return {
            "available": False,
            "learning_status": "Learning State Missing",
            "sample_note": "样本不足，不能得出稳定结论。",
        }
    sample_count = int(state.get("sample_count", 0) or 0)
    return {
        "available": True,
        "learning_status": state.get("learning_status"),
        "sample_count": sample_count,
        "drift_status": state.get("drift_status"),
        "calibration_status": state.get("calibration_status"),
        "best_model_last_20": state.get("best_model_last_20"),
        "best_model_last_60": state.get("best_model_last_60"),
        "best_model_last_150": state.get("best_model_last_150"),
        "last_20": _window(metrics, "last_20"),
        "last_60": _window(metrics, "last_60"),
        "last_150": _window(metrics, "last_150"),
        "sample_note": "样本不足，不能得出稳定结论。" if sample_count < 20 else "learning sample is available for observation.",
    }
