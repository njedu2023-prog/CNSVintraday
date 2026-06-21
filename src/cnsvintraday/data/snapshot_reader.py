from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from cnsvintraday.utils.paths import snapshot_dir


class SnapshotReader:
    def __init__(self, data_root: Path, trade_date: str, snapshot_time: str = "1400"):
        self.data_root = data_root
        self.trade_date = trade_date
        self.snapshot_time = snapshot_time
        self.base_dir = snapshot_dir(data_root, trade_date, snapshot_time)

    @property
    def paths(self) -> dict[str, Path]:
        suffix = self.snapshot_time
        return {
            "snapshot_1min": self.base_dir / f"cnsv_1min_asof_{suffix}.parquet",
            "snapshot_5min": self.base_dir / f"cnsv_5min_asof_{suffix}.parquet",
            "snapshot_15min": self.base_dir / f"cnsv_15min_asof_{suffix}.parquet",
            "snapshot_json": self.base_dir / f"intraday_snapshot_{suffix}.json",
            "quality": self.base_dir / f"intraday_quality_{suffix}.json",
            "manifest": self.base_dir / f"intraday_manifest_{suffix}.json",
        }

    def check_files(self) -> dict[str, bool]:
        return {name: path.exists() for name, path in self.paths.items()}

    def read_json_file(self, name: str) -> dict[str, Any]:
        path = self.paths[name]
        if not path.exists():
            raise FileNotFoundError(f"snapshot JSON missing: {path}")
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError(f"{path} must contain a JSON object")
        return data

    def read_minutes(self, name: str = "snapshot_1min") -> pd.DataFrame:
        path = self.paths[name]
        if not path.exists():
            raise FileNotFoundError(f"snapshot parquet missing: {path}")
        return pd.read_parquet(path)
