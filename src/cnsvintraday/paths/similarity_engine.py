from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from cnsvintraday.models.baseline_models import FEATURE_METADATA_COLUMNS
from cnsvintraday.validation.future_guard import check_no_future_columns


PATH_NON_FEATURE_COLUMNS = FEATURE_METADATA_COLUMNS | {
    "price_1400",
    "label_up_t1",
    "label_return_t1",
}


def path_feature_columns(frame: pd.DataFrame) -> list[str]:
    columns = [column for column in frame.columns if column not in PATH_NON_FEATURE_COLUMNS]
    violations = check_no_future_columns(columns)
    if violations:
        raise ValueError(f"future guard failed for path features: {violations}")
    return columns


@dataclass(frozen=True)
class SimilarityConfig:
    lookback_days: int = 150
    sample_count: int = 20


def standardize_history(history: pd.DataFrame, current: pd.Series, feature_names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    if not feature_names:
        raise ValueError("path similarity requires at least one feature")
    x_history = history[feature_names].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float)
    x_current = pd.DataFrame([current[feature_names]]).apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float)
    means = x_history.mean(axis=0)
    stds = x_history.std(axis=0)
    stds[stds == 0.0] = 1.0
    return (x_history - means) / stds, (x_current - means) / stds


def find_similar_samples(
    history: pd.DataFrame,
    current: pd.Series,
    feature_names: list[str] | None = None,
    sample_count: int = 20,
) -> pd.DataFrame:
    if history.empty:
        raise ValueError("path similarity history is empty")
    if "label_return_t1" not in history.columns:
        raise ValueError("path similarity history missing label_return_t1")

    columns = feature_names or path_feature_columns(history)
    x_history, x_current = standardize_history(history, current, columns)
    distances = np.linalg.norm(x_history - x_current, axis=1)

    samples = history[["trade_date", "label_return_t1"]].copy()
    samples["distance"] = distances
    samples = samples.sort_values(["distance", "trade_date"], kind="mergesort").head(sample_count)
    samples["similarity_rank"] = range(1, len(samples) + 1)
    return samples[["similarity_rank", "trade_date", "distance", "label_return_t1"]].reset_index(drop=True)

