from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from cnsvintraday.models.metrics import evaluate_predictions


def build_model_leaderboard(predictions: pd.DataFrame) -> dict[str, Any]:
    rows = []
    for model_name, group in predictions.groupby("model_name"):
        metrics = evaluate_predictions(group)
        rows.append(
            {
                "model_name": model_name,
                "training_date": str(group["trade_date"].max()),
                "auc": metrics["auc"],
                "brier": metrics["brier"],
                "rmse": metrics["rmse"],
                "mae": metrics["mae"],
                "hit_rate": metrics["hit_rate"],
                "calibration": metrics["calibration"],
            }
        )
    rows.sort(key=lambda row: row["model_name"])
    return {"models": rows}


def write_model_leaderboard(predictions: pd.DataFrame, path: Path) -> dict[str, Any]:
    leaderboard = build_model_leaderboard(predictions)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(leaderboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return leaderboard
