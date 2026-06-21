from __future__ import annotations

import json

import pandas as pd

from cnsvintraday.models.baseline_pipeline import main
from cnsvintraday.models.labels import build_t1_labels
from cnsvintraday.models.replay_engine import baseline_output_paths, build_baseline_outputs, run_replay

from model_helpers import make_feature_frame, make_label_source


def test_replay_engine_outputs_b0_to_b3_predictions() -> None:
    features = make_feature_frame(151)
    labels = build_t1_labels(make_label_source(151))

    replay = run_replay(features, labels, train_window=150)

    assert set(replay["model_name"]) == {"B0", "B1", "B2", "B3"}
    assert len(replay) == 4
    assert {"prob_up", "prob_down", "expected_return", "confidence", "label_up_t1", "label_return_t1"}.issubset(replay.columns)


def test_baseline_pipeline_writes_outputs(tmp_path) -> None:
    feature_path = tmp_path / "data" / "features" / "feature_snapshot_1400.parquet"
    label_path = tmp_path / "data" / "labels" / "label_source.parquet"
    feature_path.parent.mkdir(parents=True)
    label_path.parent.mkdir(parents=True)
    make_feature_frame(151).to_parquet(feature_path, index=False)
    make_label_source(151).to_parquet(label_path, index=False)

    exit_code = main(
        [
            "--data-root",
            str(tmp_path),
            "--label-source-path",
            "data/labels/label_source.parquet",
            "--train-window",
            "150",
        ]
    )
    paths = baseline_output_paths(tmp_path)

    assert exit_code == 0
    assert paths["prediction"].is_file()
    assert paths["leaderboard"].is_file()
    assert paths["replay"].is_file()
    assert paths["dashboard"].is_file()

    predictions = pd.read_parquet(paths["prediction"])
    leaderboard = json.loads(paths["leaderboard"].read_text(encoding="utf-8"))
    dashboard = paths["dashboard"].read_text(encoding="utf-8")

    assert set(predictions["model_name"]) == {"B0", "B1", "B2", "B3"}
    assert "label_up_t1" not in predictions.columns
    assert {item["model_name"] for item in leaderboard["models"]} == {"B0", "B1", "B2", "B3"}
    assert "CNSVintraday V1.3 Baseline Dashboard" in dashboard


def test_build_baseline_outputs_rejects_short_history(tmp_path) -> None:
    features = make_feature_frame(50)
    labels = build_t1_labels(make_label_source(50))

    try:
        build_baseline_outputs(tmp_path, features, labels)
    except ValueError as error:
        assert "history insufficient" in str(error)
    else:
        raise AssertionError("short history should fail")
