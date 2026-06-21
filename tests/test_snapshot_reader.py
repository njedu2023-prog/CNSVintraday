from pathlib import Path

from cnsvintraday.data.snapshot_reader import SnapshotReader


def test_snapshot_reader_checks_expected_files(tmp_path: Path) -> None:
    base = tmp_path / "data/intraday/snapshots/20260622/1400"
    base.mkdir(parents=True)
    (base / "intraday_quality_1400.json").write_text("{}", encoding="utf-8")

    checks = SnapshotReader(tmp_path, "20260622").check_files()

    assert checks["quality"] is True
    assert checks["snapshot_1min"] is False
    assert checks["manifest"] is False
