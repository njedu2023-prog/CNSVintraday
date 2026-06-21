from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from cnsvintraday.validation.future_guard import check_no_future_columns


FEATURE_METADATA_COLUMNS = {"trade_date", "snapshot_time", "ts_code"}


def sigmoid(value: float) -> float:
    clipped = max(min(value, 40.0), -40.0)
    return float(1.0 / (1.0 + math.exp(-clipped)))


def feature_columns(frame: pd.DataFrame) -> list[str]:
    columns = [column for column in frame.columns if column not in FEATURE_METADATA_COLUMNS]
    violations = check_no_future_columns(columns)
    if violations:
        raise ValueError(f"future guard failed for model features: {violations}")
    return columns


def _prediction(model_name: str, row: pd.Series, prob_up: float, expected_return: float) -> dict[str, object]:
    prob = max(min(float(prob_up), 0.99), 0.01)
    return {
        "trade_date": str(row["trade_date"]),
        "next_trade_date": str(row.get("next_trade_date", "")),
        "model_name": model_name,
        "prob_up": prob,
        "prob_down": 1.0 - prob,
        "expected_return": float(expected_return),
        "confidence": abs(prob - 0.5) * 2.0,
    }


class RandomBaselineModel:
    name = "B0"

    def predict_one(self, row: pd.Series) -> dict[str, object]:
        digest = hashlib.sha256(str(row["trade_date"]).encode("utf-8")).hexdigest()
        raw = int(digest[:8], 16) / 0xFFFFFFFF
        return _prediction(self.name, row, 0.25 + raw * 0.5, 0.0)


class PersistenceBaselineModel:
    name = "B1"

    def predict_one(self, row: pd.Series) -> dict[str, object]:
        momentum = float(pd.Series([row.get("return_15m", 0.0), row.get("return_30m", 0.0), row.get("return_60m", 0.0)]).mean())
        return _prediction(self.name, row, sigmoid(momentum * 25.0), momentum)


class MeanReversionBaselineModel:
    name = "B2"

    def predict_one(self, row: pd.Series) -> dict[str, object]:
        distance = float(row.get("distance_to_vwap", 0.0))
        close_position = float(row.get("close_position", 0.5))
        score = -distance * 20.0 + (0.5 - close_position) * 1.5
        return _prediction(self.name, row, sigmoid(score), -distance * 0.2)


@dataclass
class LogisticRegressionBaselineModel:
    feature_names: list[str] | None = None
    weights: np.ndarray | None = None
    bias: float = 0.0
    return_weights: np.ndarray | None = None
    return_bias: float = 0.0
    means: np.ndarray | None = None
    stds: np.ndarray | None = None
    min_history: int = 150
    name: str = "B3"

    def fit(self, frame: pd.DataFrame, feature_names_: Iterable[str], learning_rate: float = 0.1, steps: int = 250) -> None:
        if len(frame) < self.min_history:
            raise ValueError(f"history insufficient for B3 training: need {self.min_history}, got {len(frame)}")
        self.feature_names = list(feature_names_)
        violations = check_no_future_columns(self.feature_names)
        if violations:
            raise ValueError(f"future guard failed for B3 features: {violations}")

        x = frame[self.feature_names].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float)
        y = frame["label_up_t1"].to_numpy(dtype=float)
        self.means = x.mean(axis=0)
        self.stds = x.std(axis=0)
        self.stds[self.stds == 0] = 1.0
        x = self._standardize(x)
        weights = np.zeros(x.shape[1], dtype=float)
        bias = 0.0
        for _ in range(steps):
            scores = np.clip(x @ weights + bias, -40, 40)
            preds = 1.0 / (1.0 + np.exp(-scores))
            error = preds - y
            weights -= learning_rate * (x.T @ error / len(y))
            bias -= learning_rate * float(error.mean())
        self.weights = weights
        self.bias = bias

        returns = frame["label_return_t1"].to_numpy(dtype=float)
        design = np.column_stack([np.ones(len(x)), x])
        coeffs = np.linalg.pinv(design) @ returns
        self.return_bias = float(coeffs[0])
        self.return_weights = coeffs[1:]

    def _standardize(self, values: np.ndarray) -> np.ndarray:
        if self.means is None or self.stds is None:
            return values
        return (values - self.means) / self.stds

    def predict_one(self, row: pd.Series) -> dict[str, object]:
        if self.feature_names is None or self.weights is None or self.return_weights is None:
            raise ValueError("B3 model is not trained")
        x = pd.DataFrame([row[self.feature_names]]).apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float)
        x = self._standardize(x)
        prob_up = sigmoid(float((x @ self.weights + self.bias)[0]))
        expected_return = float((x @ self.return_weights + self.return_bias)[0])
        return _prediction(self.name, row, prob_up, expected_return)


def predict_rule_based(row: pd.Series) -> list[dict[str, object]]:
    return [
        RandomBaselineModel().predict_one(row),
        PersistenceBaselineModel().predict_one(row),
        MeanReversionBaselineModel().predict_one(row),
    ]
