from pathlib import Path

from cnsvintraday.data.snapshot_reader import SnapshotReader


def test_snapshot_paths_are_dynamic_for_supported_times(tmp_path: Path) -> None:
    for snapshot_time in ("1030", "1100", "1330", "1400"):
        paths = SnapshotReader(tmp_path, "20260622", snapshot_time).paths

        assert paths["snapshot_1min"] == (
            tmp_path / f"data/intraday/snapshots/20260622/{snapshot_time}/cnsv_1min_asof_{snapshot_time}.parquet"
        )
        assert paths["snapshot_5min"].name == f"cnsv_5min_asof_{snapshot_time}.parquet"
        assert paths["snapshot_15min"].name == f"cnsv_15min_asof_{snapshot_time}.parquet"
        assert paths["snapshot_json"].name == f"intraday_snapshot_{snapshot_time}.json"
        assert paths["quality"].name == f"intraday_quality_{snapshot_time}.json"
        assert paths["manifest"].name == f"intraday_manifest_{snapshot_time}.json"
