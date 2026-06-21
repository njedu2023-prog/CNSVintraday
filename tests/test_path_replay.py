from __future__ import annotations

import json

import pandas as pd

from cnsvintraday.paths.path_replay import build_path_outputs, path_output_paths, run_path_replay

from model_helpers import make_feature_frame, make_label_source


def test_path_replay_outputs_distribution_and_samples() -> None:
    replay, samples = run_path_replay(make_feature_frame(171), make_label_source(171))

    assert len(replay) == 21
    assert len(samples) == 21 * 20
    assert {"path_p10", "path_p25", "path_p50", "path_p75", "path_p90"}.issubset(replay.columns)
    assert {"price_p10", "price_p25", "price_p50", "price_p75", "price_p90"}.issubset(replay.columns)
    assert {"downside_risk", "upside_potential", "expected_range", "volatility_score"}.issubset(replay.columns)
    assert (replay["path_p10"] <= replay["path_p90"]).all()


def test_path_pipeline_writes_all_v14_outputs(tmp_path) -> None:
    features = make_feature_frame(171)
    label_source = make_label_source(171)

    result = build_path_outputs(tmp_path, features, label_source)
    paths = path_output_paths(tmp_path)

    assert result["prediction_count"] == 21
    assert result["sample_count"] == 21 * 20
    assert paths["distribution"].is_file()
    assert paths["metrics"].is_file()
    assert paths["similarity"].is_file()
    assert paths["dashboard"].is_file()

    distribution = pd.read_parquet(paths["distribution"])
    samples = pd.read_parquet(paths["similarity"])
    metrics = json.loads(paths["metrics"].read_text(encoding="utf-8"))
    dashboard = paths["dashboard"].read_text(encoding="utf-8")

    assert {"path_p10", "path_p25", "path_p50", "path_p75", "path_p90"}.issubset(distribution.columns)
    assert {"price_p10", "price_p25", "price_p50", "price_p75", "price_p90"}.issubset(distribution.columns)
    assert {"target_trade_date", "sample_trade_date", "distance", "sample_return_t1"}.issubset(samples.columns)
    assert {"coverage", "interval_width", "rmse", "calibration", "recent_20", "recent_60", "recent_150"}.issubset(metrics)
    assert "CNSVintraday V1.4 Path Dashboard" in dashboard

