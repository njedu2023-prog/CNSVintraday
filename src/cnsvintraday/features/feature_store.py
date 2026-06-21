from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from cnsvintraday.data.snapshot_reader import SnapshotReader
from cnsvintraday.features import FEATURE_VERSION
from cnsvintraday.features.common import prepare_minute_frame
from cnsvintraday.features.feature_dashboard import write_feature_dashboard
from cnsvintraday.features.feature_manifest import feature_names, write_feature_manifest
from cnsvintraday.features.feature_quality import write_feature_quality
from cnsvintraday.features.price_features import build_price_features
from cnsvintraday.features.strength_features import build_strength_features
from cnsvintraday.features.trend_features import build_trend_features
from cnsvintraday.features.volume_features import build_volume_features
from cnsvintraday.features.vwap_features import build_vwap_features
from cnsvintraday.validation.future_guard import check_minute_frame, check_no_future_columns


def build_feature_row(frame: pd.DataFrame, snapshot_time: str = "1400") -> dict[str, Any]:
    minute_frame = prepare_minute_frame(frame)
    violations = check_minute_frame(minute_frame, "14:00")
    if violations:
        raise ValueError(f"future guard failed before feature build: {violations}")

    row: dict[str, Any] = {
        "trade_date": str(minute_frame["trade_date"].iloc[-1]),
        "snapshot_time": snapshot_time,
        "ts_code": str(minute_frame["ts_code"].iloc[-1]),
    }
    row.update(build_price_features(minute_frame))
    row.update(build_volume_features(minute_frame))
    row.update(build_vwap_features(minute_frame))
    row.update(build_trend_features(minute_frame))
    row.update(build_strength_features(minute_frame))

    expected = set(feature_names())
    actual = set(row) - {"trade_date", "snapshot_time", "ts_code"}
    if actual != expected:
        raise ValueError(f"feature set mismatch missing={sorted(expected - actual)} extra={sorted(actual - expected)}")
    violations = check_no_future_columns(row.keys())
    if violations:
        raise ValueError(f"future guard failed after feature build: {violations}")
    return row


def build_feature_snapshot(frame: pd.DataFrame, snapshot_time: str = "1400") -> pd.DataFrame:
    return pd.DataFrame([build_feature_row(frame, snapshot_time=snapshot_time)])


def feature_output_paths(data_root: Path, snapshot_time: str = "1400") -> dict[str, Path]:
    feature_dir = data_root / "data" / "features"
    return {
        "snapshot": feature_dir / f"feature_snapshot_{snapshot_time}.parquet",
        "manifest": feature_dir / "feature_manifest.json",
        "quality": feature_dir / "feature_quality_latest.json",
        "dashboard": data_root / "docs" / "features" / "feature_dashboard.html",
    }


def build_feature_store(data_root: Path, trade_date: str, snapshot_time: str = "1400") -> dict[str, Any]:
    reader = SnapshotReader(data_root, trade_date, snapshot_time)
    minute_frame = reader.read_minutes("snapshot_1min")
    feature_frame = build_feature_snapshot(minute_frame, snapshot_time=snapshot_time)
    paths = feature_output_paths(data_root, snapshot_time)
    paths["snapshot"].parent.mkdir(parents=True, exist_ok=True)
    feature_frame.to_parquet(paths["snapshot"], index=False)
    manifest = write_feature_manifest(paths["manifest"])
    quality = write_feature_quality(feature_frame, paths["quality"])
    write_feature_dashboard(manifest, quality, paths["dashboard"])
    return {
        "feature_version": FEATURE_VERSION,
        "feature_count": int(manifest["feature_count"]),
        "quality_status": quality["status"],
        "paths": {key: str(value) for key, value in paths.items()},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build CNSVintraday V1.2 feature store")
    parser.add_argument("--data-root", default=".")
    parser.add_argument("--trade-date", required=True)
    parser.add_argument("--snapshot-time", default="1400")
    args = parser.parse_args(argv)
    summary = build_feature_store(Path(args.data_root), args.trade_date, args.snapshot_time)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["quality_status"] in {"PASS", "WARN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
