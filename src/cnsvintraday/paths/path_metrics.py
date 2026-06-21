from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


def _window_stats(frame: pd.DataFrame, window: int) -> dict[str, float]:
    tail = frame.tail(window)
    if tail.empty:
        return {"coverage": 0.0, "interval_width": 0.0}
    inside = (tail["label_return_t1"] >= tail["path_p10"]) & (tail["label_return_t1"] <= tail["path_p90"])
    return {
        "coverage": float(inside.mean()),
        "interval_width": float((tail["path_p90"] - tail["path_p10"]).mean()),
    }


def build_path_metrics(replay: pd.DataFrame) -> dict[str, Any]:
    if replay.empty:
        raise ValueError("path replay is empty")
    actual = replay["label_return_t1"].astype(float)
    median = replay["path_p50"].astype(float)
    errors = median - actual
    inside = (actual >= replay["path_p10"]) & (actual <= replay["path_p90"])
    width = replay["path_p90"] - replay["path_p10"]
    metrics = {
        "status": "PASS",
        "coverage": float(inside.mean()),
        "coverage_target": 0.80,
        "interval_width": float(width.mean()),
        "rmse": float(math.sqrt((errors**2).mean())),
        "calibration": float(abs(float(inside.mean()) - 0.80)),
        "sample_count": int(len(replay)),
        "recent_20": _window_stats(replay, 20),
        "recent_60": _window_stats(replay, 60),
        "recent_150": _window_stats(replay, 150),
    }
    return metrics


def write_path_metrics(replay: pd.DataFrame, path: Path) -> dict[str, Any]:
    metrics = build_path_metrics(replay)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metrics

