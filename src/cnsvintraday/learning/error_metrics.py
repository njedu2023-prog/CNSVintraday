from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


WINDOWS = {"latest": 1, "last_20": 20, "last_60": 60, "last_150": 150}


def log_loss_safe(actual: pd.Series, prob_up: pd.Series) -> float:
    probs = np.clip(np.asarray(prob_up, dtype=float), 1e-6, 1 - 1e-6)
    labels = np.asarray(actual, dtype=float)
    return float(-np.mean(labels * np.log(probs) + (1 - labels) * np.log(1 - probs)))


def _metrics_for(frame: pd.DataFrame, required_samples: int) -> dict[str, Any]:
    valid = frame[frame["joined_status"] == "JOINED"].copy()
    if len(valid) < required_samples:
        return {"sample_status": "INSUFFICIENT", "sample_count": int(len(valid)), "required_samples": required_samples}

    actual_up = valid["actual_up_t1"].astype(float)
    actual_return = valid["actual_return_t1"].astype(float)
    prob_up = valid["prob_up"].astype(float)
    expected_return = valid["expected_return"].astype(float)
    p50 = valid["path_p50"].astype(float)
    p10 = valid["path_p10"].astype(float)
    p25 = valid["path_p25"].astype(float)
    p75 = valid["path_p75"].astype(float)
    p90 = valid["path_p90"].astype(float)
    return {
        "sample_status": "OK",
        "sample_count": int(len(valid)),
        "hit_rate": float(((prob_up >= 0.5) == (actual_up == 1)).mean()),
        "brier_score": float(((prob_up - actual_up) ** 2).mean()),
        "log_loss_safe": log_loss_safe(actual_up, prob_up),
        "rmse": float(math.sqrt(((expected_return - actual_return) ** 2).mean())),
        "mae": float((expected_return - actual_return).abs().mean()),
        "mean_error": float((expected_return - actual_return).mean()),
        "median_abs_error": float((expected_return - actual_return).abs().median()),
        "coverage_p10_p90": float(((actual_return >= p10) & (actual_return <= p90)).mean()),
        "coverage_p25_p75": float(((actual_return >= p25) & (actual_return <= p75)).mean()),
        "interval_width_p10_p90": float((p90 - p10).mean()),
        "interval_width_p25_p75": float((p75 - p25).mean()),
        "p50_error": float((p50 - actual_return).mean()),
        "p50_abs_error": float((p50 - actual_return).abs().mean()),
    }


def _tail_trade_days(frame: pd.DataFrame, days: int) -> pd.DataFrame:
    if frame.empty:
        return frame
    dates = sorted(frame["trade_date"].astype(str).unique())[-days:]
    return frame[frame["trade_date"].astype(str).isin(dates)]


def build_learning_metrics(joined: pd.DataFrame) -> dict[str, Any]:
    valid = joined[joined["joined_status"] == "JOINED"].sort_values("trade_date")
    windows: dict[str, Any] = {}
    for name, size in WINDOWS.items():
        window = _tail_trade_days(valid, size)
        windows[name] = {
            "overall": _metrics_for(window, size),
            "by_model": {model: _metrics_for(group, size) for model, group in window.groupby("model_name")},
        }
    return {"status": "PASS", "joined_sample_count": int(len(valid)), "windows": windows}


def write_learning_metrics(metrics: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
