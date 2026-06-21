from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ALLOWED_USAGE = {
    "can_review_predictions": True,
    "can_update_dashboard": True,
    "can_promote_model": False,
    "can_generate_formal_signal": False,
}


def _window_status(metrics: dict[str, Any], window: str) -> str:
    return str(metrics["windows"][window]["overall"]["sample_status"])


def _best_model(metrics: dict[str, Any], window: str) -> str | None:
    candidates = []
    for model_name, values in metrics["windows"][window]["by_model"].items():
        if values.get("sample_status") == "OK":
            candidates.append((float(values["brier_score"]), model_name))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][1]


def build_learning_state(joined: pd.DataFrame, metrics: dict[str, Any], calibration: dict[str, Any], drift: dict[str, Any]) -> dict[str, Any]:
    valid = joined[joined["joined_status"] == "JOINED"]
    latest_trade_date = str(joined["trade_date"].max()) if not joined.empty else None
    latest_truth_date = str(valid["next_trade_date"].max()) if not valid.empty else None
    return {
        "learning_ready": bool(len(valid) > 0),
        "learning_status": "READY" if len(valid) > 0 else "PENDING_TRUTH",
        "latest_trade_date": latest_trade_date,
        "latest_truth_date": latest_truth_date,
        "sample_count": int(len(valid)),
        "last_20_status": _window_status(metrics, "last_20"),
        "last_60_status": _window_status(metrics, "last_60"),
        "last_150_status": _window_status(metrics, "last_150"),
        "best_model_last_20": _best_model(metrics, "last_20"),
        "best_model_last_60": _best_model(metrics, "last_60"),
        "best_model_last_150": _best_model(metrics, "last_150"),
        "drift_status": drift["drift_status"],
        "calibration_status": calibration["sample_status"],
        "allowed_usage": ALLOWED_USAGE,
    }


def write_learning_state(state: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path

