from __future__ import annotations

import json

from cnsvintraday.learning.build_learning import build_learning_outputs

from learning_helpers import make_path_frame, make_prediction_frame, make_truth_frame
from model_helpers import make_feature_frame


def make_context(trade_date: str = "20260025", next_trade_date: str = "20260026") -> dict:
    return {
        "trade_date": trade_date,
        "next_trade_date": next_trade_date,
        "snapshot_time": "1400",
        "ready": True,
        "status": "PASS",
        "allowed_to_run": True,
        "future_guard_passed": True,
        "formal_signal_allowed": False,
    }


def write_decision_inputs(root, days: int = 25, with_optional: bool = True) -> None:
    context = make_context()
    context_path = root / "data" / "runtime" / "context" / "intraday_context_latest.json"
    context_path.parent.mkdir(parents=True)
    context_path.write_text(json.dumps(context, ensure_ascii=False), encoding="utf-8")

    feature_path = root / "data" / "features" / "feature_snapshot_1400.parquet"
    feature_path.parent.mkdir(parents=True)
    make_feature_frame(days).tail(1).to_parquet(feature_path, index=False)

    predictions = make_prediction_frame(days)
    prediction_path = root / "data" / "models" / "prediction_snapshot_1400.parquet"
    prediction_path.parent.mkdir(parents=True)
    predictions.tail(2).to_parquet(prediction_path, index=False)

    path_frame = make_path_frame(days)
    path_path = root / "data" / "paths" / "path_distribution_latest.parquet"
    path_path.parent.mkdir(parents=True)
    path_frame.tail(1).to_parquet(path_path, index=False)

    build_learning_outputs(root, predictions, path_frame, make_truth_frame(days))

    if with_optional:
        (root / "data" / "features" / "feature_quality_latest.json").write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
        (root / "data" / "models" / "model_leaderboard.json").write_text(
            json.dumps({"models": [{"model_name": "B0", "brier": 0.3}, {"model_name": "B1", "brier": 0.1}]}),
            encoding="utf-8",
        )
        (root / "data" / "paths" / "path_metrics_latest.json").write_text(json.dumps({"coverage": 0.9}), encoding="utf-8")
