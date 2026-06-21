from __future__ import annotations

import json

import pandas as pd
import pytest

from cnsvintraday.features.feature_manifest import feature_names
from cnsvintraday.features.feature_store import build_feature_snapshot, build_feature_store, feature_output_paths

from feature_helpers import make_minute_frame


def test_feature_snapshot_matches_manifest() -> None:
    snapshot = build_feature_snapshot(make_minute_frame(), snapshot_time="1400")

    assert len(snapshot) == 1
    assert set(feature_names()).issubset(snapshot.columns)
    assert snapshot["snapshot_time"].iloc[0] == "1400"
    assert not any("future" in column for column in snapshot.columns)


def test_feature_store_writes_contract_outputs(tmp_path) -> None:
    source = make_minute_frame()
    snapshot_dir = tmp_path / "data" / "intraday" / "snapshots" / "20260622" / "1400"
    snapshot_dir.mkdir(parents=True)
    source.to_parquet(snapshot_dir / "cnsv_1min_asof_1400.parquet", index=False)

    summary = build_feature_store(tmp_path, "20260622", "1400")
    paths = feature_output_paths(tmp_path, "1400")

    assert summary["feature_count"] == len(feature_names())
    assert summary["quality_status"] == "PASS"
    assert all(path.exists() for path in paths.values())

    feature_frame = pd.read_parquet(paths["snapshot"])
    quality = json.loads(paths["quality"].read_text(encoding="utf-8"))
    dashboard = paths["dashboard"].read_text(encoding="utf-8")

    assert len(feature_frame) == 1
    assert quality["status"] == "PASS"
    assert "Contract Summary" in dashboard


def test_feature_store_rejects_after_1400_rows() -> None:
    frame = make_minute_frame()
    frame.loc[len(frame)] = frame.iloc[-1]
    frame.loc[len(frame) - 1, "trade_time"] = pd.Timestamp("2026-06-22 14:01:00")

    with pytest.raises(ValueError, match="future guard failed"):
        build_feature_snapshot(frame, snapshot_time="1400")
