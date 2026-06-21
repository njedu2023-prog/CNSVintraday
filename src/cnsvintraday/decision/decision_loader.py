from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class DecisionInputs:
    data_root: Path
    snapshot_time: str = "1400"
    context: dict[str, Any] | None = None
    feature_snapshot: pd.DataFrame | None = None
    feature_quality: dict[str, Any] | None = None
    prediction_snapshot: pd.DataFrame | None = None
    model_leaderboard: dict[str, Any] | None = None
    path_distribution: pd.DataFrame | None = None
    path_metrics: dict[str, Any] | None = None
    learning_state: dict[str, Any] | None = None
    learning_metrics: dict[str, Any] | None = None
    missing_files: list[str] = field(default_factory=list)
    warning_messages: list[str] = field(default_factory=list)
    fail_reasons: list[str] = field(default_factory=list)


def decision_input_paths(data_root: Path, snapshot_time: str = "1400") -> dict[str, Path]:
    return {
        "context": data_root / "data" / "runtime" / "context" / "intraday_context_latest.json",
        "feature_snapshot": data_root / "data" / "features" / f"feature_snapshot_{snapshot_time}.parquet",
        "feature_quality": data_root / "data" / "features" / "feature_quality_latest.json",
        "prediction_snapshot": data_root / "data" / "models" / f"prediction_snapshot_{snapshot_time}.parquet",
        "model_leaderboard": data_root / "data" / "models" / "model_leaderboard.json",
        "path_distribution": data_root / "data" / "paths" / "path_distribution_latest.parquet",
        "path_metrics": data_root / "data" / "paths" / "path_metrics_latest.json",
        "learning_state": data_root / "metadata" / "learning_state_latest.json",
        "learning_metrics": data_root / "data" / "learning" / "learning_metrics_latest.json",
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_decision_inputs(data_root: Path, snapshot_time: str = "1400") -> DecisionInputs:
    data_root = Path(data_root)
    inputs = DecisionInputs(data_root=data_root, snapshot_time=snapshot_time)
    paths = decision_input_paths(data_root, snapshot_time=snapshot_time)
    critical = {"context", "feature_snapshot", "prediction_snapshot", "path_distribution"}
    json_files = {"context", "feature_quality", "model_leaderboard", "path_metrics", "learning_state", "learning_metrics"}
    parquet_files = {"feature_snapshot", "prediction_snapshot", "path_distribution"}

    for name, path in paths.items():
        if not path.exists():
            inputs.missing_files.append(str(path))
            if name in critical:
                inputs.fail_reasons.append(f"missing critical file: {name}")
            else:
                inputs.warning_messages.append(f"missing optional file: {name}")
            continue
        try:
            if name in json_files:
                setattr(inputs, name, _read_json(path))
            elif name in parquet_files:
                setattr(inputs, name, pd.read_parquet(path))
        except Exception as exc:
            inputs.fail_reasons.append(f"failed to read {name}: {exc}")
    return inputs
