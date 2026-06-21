from __future__ import annotations

import json

import pandas as pd

from cnsvintraday.learning.build_learning import build_learning_outputs, learning_output_paths, main

from learning_helpers import make_path_frame, make_prediction_frame, make_truth_frame


def test_build_learning_pipeline_writes_all_outputs(tmp_path) -> None:
    result = build_learning_outputs(tmp_path, make_prediction_frame(25), make_path_frame(25), make_truth_frame(25))
    paths = learning_output_paths(tmp_path)

    assert result["prediction_count"] == 50
    assert result["joined_count"] == 50
    for path in paths.values():
        assert path.is_file()

    log = pd.read_parquet(paths["prediction_log"])
    joined = pd.read_parquet(paths["joined"])
    metrics = json.loads(paths["metrics"].read_text(encoding="utf-8"))
    state = json.loads(paths["state"].read_text(encoding="utf-8"))

    assert log["formal_signal_allowed"].eq(False).all()
    assert joined["joined_status"].eq("JOINED").all()
    assert metrics["windows"]["last_20"]["overall"]["sample_status"] == "OK"
    assert state["allowed_usage"]["can_generate_formal_signal"] is False


def test_build_learning_cli_allows_missing_truth_pending(tmp_path) -> None:
    prediction_path = tmp_path / "data" / "models" / "prediction_snapshot_1400.parquet"
    path_distribution_path = tmp_path / "data" / "paths" / "path_distribution_latest.parquet"
    prediction_path.parent.mkdir(parents=True)
    path_distribution_path.parent.mkdir(parents=True)
    make_prediction_frame(2).to_parquet(prediction_path, index=False)
    make_path_frame(2).to_parquet(path_distribution_path, index=False)

    exit_code = main(["--data-root", str(tmp_path), "--snapshot-time", "1400"])

    state = json.loads((tmp_path / "metadata" / "learning_state_latest.json").read_text(encoding="utf-8"))
    joined = pd.read_parquet(tmp_path / "data" / "learning" / "prediction_truth_joined_latest.parquet")
    assert exit_code == 0
    assert state["learning_status"] == "PENDING_TRUTH"
    assert joined["joined_status"].eq("PENDING_TRUTH").all()

