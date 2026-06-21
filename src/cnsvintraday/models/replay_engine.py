from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from cnsvintraday.models import BASELINE_MODEL_VERSION
from cnsvintraday.models.baseline_dashboard import write_baseline_dashboard
from cnsvintraday.models.baseline_models import (
    LogisticRegressionBaselineModel,
    feature_columns,
    predict_rule_based,
)
from cnsvintraday.models.leaderboard import write_model_leaderboard


def prepare_model_frame(features: pd.DataFrame, labels: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    columns = feature_columns(features)
    merged = features.merge(labels, on="trade_date", how="inner").sort_values("trade_date").reset_index(drop=True)
    if merged.empty:
        raise ValueError("model frame is empty after joining features and labels")
    return merged, columns


def run_replay(features: pd.DataFrame, labels: pd.DataFrame, train_window: int = 150) -> pd.DataFrame:
    model_frame, columns = prepare_model_frame(features, labels)
    if len(model_frame) <= train_window:
        raise ValueError(f"history insufficient for replay: need more than {train_window}, got {len(model_frame)}")

    predictions: list[dict[str, object]] = []
    for index in range(train_window, len(model_frame)):
        train = model_frame.iloc[index - train_window : index]
        row = model_frame.iloc[index]
        predictions.extend(predict_rule_based(row))

        logistic = LogisticRegressionBaselineModel(min_history=train_window)
        logistic.fit(train, columns)
        predictions.append(logistic.predict_one(row))

    prediction_frame = pd.DataFrame(predictions)
    labels_for_eval = model_frame[["trade_date", "label_up_t1", "label_return_t1"]]
    return prediction_frame.merge(labels_for_eval, on="trade_date", how="left")


def baseline_output_paths(data_root: Path, snapshot_time: str = "1400") -> dict[str, Path]:
    return {
        "prediction": data_root / "data" / "models" / f"prediction_snapshot_{snapshot_time}.parquet",
        "leaderboard": data_root / "data" / "models" / "model_leaderboard.json",
        "replay": data_root / "data" / "replay" / "baseline_replay_latest.parquet",
        "dashboard": data_root / "docs" / "models" / "baseline_dashboard.html",
    }


def build_baseline_outputs(
    data_root: Path,
    features: pd.DataFrame,
    labels: pd.DataFrame,
    snapshot_time: str = "1400",
    train_window: int = 150,
) -> dict[str, Any]:
    replay = run_replay(features, labels, train_window=train_window)
    output = replay.drop(columns=["label_up_t1", "label_return_t1"])
    paths = baseline_output_paths(data_root, snapshot_time=snapshot_time)
    paths["prediction"].parent.mkdir(parents=True, exist_ok=True)
    paths["replay"].parent.mkdir(parents=True, exist_ok=True)
    output.to_parquet(paths["prediction"], index=False)
    replay.to_parquet(paths["replay"], index=False)
    leaderboard = write_model_leaderboard(replay, paths["leaderboard"])
    write_baseline_dashboard(leaderboard, paths["dashboard"])
    return {
        "baseline_model_version": BASELINE_MODEL_VERSION,
        "prediction_count": int(len(output)),
        "model_count": int(output["model_name"].nunique()),
        "paths": {key: str(path) for key, path in paths.items()},
    }
