from __future__ import annotations

from cnsvintraday.models.labels import build_t1_labels
from cnsvintraday.models.leaderboard import build_model_leaderboard
from cnsvintraday.models.replay_engine import run_replay

from model_helpers import make_feature_frame, make_label_source


def test_model_leaderboard_contains_required_metrics() -> None:
    replay = run_replay(make_feature_frame(151), build_t1_labels(make_label_source(151)), train_window=150)

    leaderboard = build_model_leaderboard(replay)

    assert {item["model_name"] for item in leaderboard["models"]} == {"B0", "B1", "B2", "B3"}
    for item in leaderboard["models"]:
        assert {"auc", "brier", "rmse", "mae", "hit_rate", "calibration"}.issubset(item)
