from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from cnsvintraday.learning import LEARNING_VERSION
from cnsvintraday.learning.calibration_tracker import build_calibration, write_calibration
from cnsvintraday.learning.error_metrics import build_learning_metrics, write_learning_metrics
from cnsvintraday.learning.learning_dashboard import write_learning_dashboard
from cnsvintraday.learning.learning_state import build_learning_state, write_learning_state
from cnsvintraday.learning.model_drift_monitor import build_model_drift, write_model_drift
from cnsvintraday.learning.prediction_log import build_prediction_log, write_prediction_log
from cnsvintraday.learning.truth_joiner import join_prediction_truth, write_prediction_truth_joined


def learning_output_paths(data_root: Path) -> dict[str, Path]:
    return {
        "prediction_log": data_root / "data" / "learning" / "prediction_log_latest.parquet",
        "joined": data_root / "data" / "learning" / "prediction_truth_joined_latest.parquet",
        "metrics": data_root / "data" / "learning" / "learning_metrics_latest.json",
        "calibration": data_root / "data" / "learning" / "calibration_latest.json",
        "drift": data_root / "data" / "learning" / "model_drift_latest.json",
        "state": data_root / "metadata" / "learning_state_latest.json",
        "dashboard": data_root / "docs" / "learning" / "learning_dashboard.html",
    }


def build_learning_outputs(
    data_root: Path,
    predictions: pd.DataFrame,
    paths: pd.DataFrame,
    truth: pd.DataFrame | None = None,
    snapshot_time: str = "1400",
) -> dict[str, Any]:
    outputs = learning_output_paths(data_root)
    log = build_prediction_log(predictions, paths, snapshot_time=snapshot_time)
    write_prediction_log(data_root, log, snapshot_time=snapshot_time)
    joined = join_prediction_truth(log, truth)
    write_prediction_truth_joined(data_root, joined)
    metrics = build_learning_metrics(joined)
    calibration = build_calibration(joined)
    drift = build_model_drift(metrics)
    state = build_learning_state(joined, metrics, calibration, drift)
    write_learning_metrics(metrics, outputs["metrics"])
    write_calibration(calibration, outputs["calibration"])
    write_model_drift(drift, outputs["drift"])
    write_learning_state(state, outputs["state"])
    write_learning_dashboard(state, metrics, calibration, drift, outputs["dashboard"])
    return {
        "learning_version": LEARNING_VERSION,
        "prediction_count": int(len(log)),
        "joined_count": int((joined["joined_status"] == "JOINED").sum()),
        "learning_status": state["learning_status"],
        "paths": {key: str(path) for key, path in outputs.items()},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build CNSVintraday V1.5 self learning outputs.")
    parser.add_argument("--data-root", default=".")
    parser.add_argument("--snapshot-time", default="1400")
    parser.add_argument("--prediction-path", default="data/models/prediction_snapshot_1400.parquet")
    parser.add_argument("--path-distribution-path", default="data/paths/path_distribution_latest.parquet")
    parser.add_argument("--truth-path", default="data/labels/t1_truth/t1_truth_vs_1400_latest.parquet")
    args = parser.parse_args(argv)

    data_root = Path(args.data_root)
    predictions = pd.read_parquet(data_root / args.prediction_path)
    paths = pd.read_parquet(data_root / args.path_distribution_path)
    truth_file = data_root / args.truth_path
    truth = pd.read_parquet(truth_file) if truth_file.exists() else None
    build_learning_outputs(data_root, predictions, paths, truth, snapshot_time=args.snapshot_time)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

