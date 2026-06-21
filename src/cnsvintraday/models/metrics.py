from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


def auc_score(y_true: pd.Series, prob_up: pd.Series) -> float:
    labels = np.asarray(y_true, dtype=float)
    scores = np.asarray(prob_up, dtype=float)
    positives = labels == 1
    negatives = labels == 0
    if positives.sum() == 0 or negatives.sum() == 0:
        return 0.5

    order = np.argsort(scores)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(scores) + 1)
    pos_rank_sum = ranks[positives].sum()
    return float((pos_rank_sum - positives.sum() * (positives.sum() + 1) / 2) / (positives.sum() * negatives.sum()))


def brier_score(y_true: pd.Series, prob_up: pd.Series) -> float:
    errors = np.asarray(prob_up, dtype=float) - np.asarray(y_true, dtype=float)
    return float(np.mean(errors * errors))


def rmse(y_true: pd.Series, expected_return: pd.Series) -> float:
    errors = np.asarray(expected_return, dtype=float) - np.asarray(y_true, dtype=float)
    return float(math.sqrt(np.mean(errors * errors)))


def mae(y_true: pd.Series, expected_return: pd.Series) -> float:
    errors = np.asarray(expected_return, dtype=float) - np.asarray(y_true, dtype=float)
    return float(np.mean(np.abs(errors)))


def hit_rate(y_true: pd.Series, prob_up: pd.Series) -> float:
    predicted = np.asarray(prob_up, dtype=float) >= 0.5
    observed = np.asarray(y_true, dtype=float) == 1
    return float(np.mean(predicted == observed))


def calibration(y_true: pd.Series, prob_up: pd.Series) -> dict[str, Any]:
    labels = np.asarray(y_true, dtype=float)
    probs = np.asarray(prob_up, dtype=float)
    bins = []
    for low, high in ((0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.01)):
        mask = (probs >= low) & (probs < high)
        if not mask.any():
            bins.append({"range": f"{low:.2f}-{min(high, 1.0):.2f}", "count": 0, "avg_prob": None, "actual_rate": None})
            continue
        bins.append(
            {
                "range": f"{low:.2f}-{min(high, 1.0):.2f}",
                "count": int(mask.sum()),
                "avg_prob": float(probs[mask].mean()),
                "actual_rate": float(labels[mask].mean()),
            }
        )
    return {"bins": bins}


def evaluate_predictions(frame: pd.DataFrame) -> dict[str, Any]:
    return {
        "auc": auc_score(frame["label_up_t1"], frame["prob_up"]),
        "brier": brier_score(frame["label_up_t1"], frame["prob_up"]),
        "rmse": rmse(frame["label_return_t1"], frame["expected_return"]),
        "mae": mae(frame["label_return_t1"], frame["expected_return"]),
        "hit_rate": hit_rate(frame["label_up_t1"], frame["prob_up"]),
        "calibration": calibration(frame["label_up_t1"], frame["prob_up"]),
    }
