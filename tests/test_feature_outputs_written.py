from __future__ import annotations

import json

import pandas as pd

from cnsvintraday.features.feature_manifest import feature_names
from cnsvintraday.features.feature_store import feature_output_paths, main
from cnsvintraday.validation.future_guard import FUTURE_FIELD_BLACKLIST

from feature_helpers import make_minute_frame


def test_feature_pipeline_writes_all_v12_outputs(tmp_path) -> None:
    snapshot_dir = tmp_path / "data" / "intraday" / "snapshots" / "20260622" / "1400"
    snapshot_dir.mkdir(parents=True)
    make_minute_frame().to_parquet(snapshot_dir / "cnsv_1min_asof_1400.parquet", index=False)

    exit_code = main(["--data-root", str(tmp_path), "--trade-date", "20260622", "--snapshot-time", "1400"])

    paths = feature_output_paths(tmp_path, "1400")
    assert exit_code == 0
    assert paths["snapshot"].is_file()
    assert paths["manifest"].is_file()
    assert paths["quality"].is_file()
    assert paths["dashboard"].is_file()

    feature_frame = pd.read_parquet(paths["snapshot"])
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    quality = json.loads(paths["quality"].read_text(encoding="utf-8"))
    dashboard = paths["dashboard"].read_text(encoding="utf-8")

    feature_columns = [column for column in feature_frame.columns if column not in {"trade_date", "snapshot_time", "ts_code"}]
    manifest_features = [item["feature_name"] for item in manifest["features"]]

    assert list(feature_frame["snapshot_time"]) == ["1400"]
    assert feature_frame["trade_date"].iloc[0] == "20260622"
    assert 30 <= len(feature_columns) <= 50
    assert set(feature_columns) == set(feature_names()) == set(manifest_features)
    assert manifest["feature_count"] == len(feature_columns)
    assert quality["status"] == "PASS"
    assert quality["feature_count"] == len(feature_columns)
    assert {"missing_rates", "nan_columns", "inf_columns", "constant_columns", "duplicate_columns"}.issubset(quality)
    assert "CNSVintraday V1.2 Feature Dashboard" in dashboard

    normalized_columns = [column.lower() for column in feature_frame.columns]
    for forbidden in FUTURE_FIELD_BLACKLIST:
        assert all(forbidden not in column for column in normalized_columns)
