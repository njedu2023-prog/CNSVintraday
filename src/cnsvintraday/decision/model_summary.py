from __future__ import annotations

from typing import Any

import pandas as pd


def build_model_summary(predictions: pd.DataFrame | None, leaderboard: dict[str, Any] | None = None) -> dict[str, Any]:
    if predictions is None or predictions.empty:
        return {"best_model": None, "models": [], "model_advantage_note": "prediction snapshot missing"}
    rows = predictions.sort_values(["confidence", "prob_up"], ascending=False).to_dict("records")
    best = rows[0]
    leaderboard_rows = {row.get("model_name"): row for row in (leaderboard or {}).get("models", [])}
    random_brier = leaderboard_rows.get("B0", {}).get("brier")
    best_brier = leaderboard_rows.get(best["model_name"], {}).get("brier")
    advantage = best_brier is not None and random_brier is not None and float(best_brier) < float(random_brier)
    return {
        "best_model": best["model_name"],
        "selected_prediction": {
            "prob_up": float(best["prob_up"]),
            "prob_down": float(best["prob_down"]),
            "expected_return": float(best["expected_return"]),
            "confidence": float(best["confidence"]),
        },
        "models": rows,
        "leaderboard": list(leaderboard_rows.values()),
        "better_than_random": bool(advantage),
        "model_advantage_note": "current model advantage is limited; observe only" if not advantage else "selected model is ahead of B0 on leaderboard",
    }
