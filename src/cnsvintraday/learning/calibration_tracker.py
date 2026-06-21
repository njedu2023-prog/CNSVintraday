from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def build_calibration(joined: pd.DataFrame, min_samples: int = 20) -> dict[str, Any]:
    valid = joined[joined["joined_status"] == "JOINED"].copy()
    if len(valid) < min_samples:
        return {
            "sample_status": "INSUFFICIENT",
            "sample_count": int(len(valid)),
            "required_samples": min_samples,
            "calibration_bins": [],
            "calibration_error": None,
            "over_confidence_flag": False,
            "under_confidence_flag": False,
        }

    probs = valid["prob_up"].astype(float).to_numpy()
    actual = valid["actual_up_t1"].astype(float).to_numpy()
    bins = []
    errors = []
    for index in range(10):
        low = index / 10
        high = (index + 1) / 10
        if index == 9:
            mask = (probs >= low) & (probs <= high)
        else:
            mask = (probs >= low) & (probs < high)
        if not mask.any():
            bins.append({"range": f"{low:.1f}-{high:.1f}", "bin_predicted_prob": None, "bin_actual_rate": None, "bin_count": 0})
            continue
        predicted = float(probs[mask].mean())
        rate = float(actual[mask].mean())
        count = int(mask.sum())
        errors.append(abs(predicted - rate) * count)
        bins.append({"range": f"{low:.1f}-{high:.1f}", "bin_predicted_prob": predicted, "bin_actual_rate": rate, "bin_count": count})
    calibration_error = float(sum(errors) / len(valid))
    avg_prob = float(np.mean(probs))
    avg_actual = float(np.mean(actual))
    return {
        "sample_status": "OK",
        "sample_count": int(len(valid)),
        "calibration_bins": bins,
        "calibration_error": calibration_error,
        "over_confidence_flag": avg_prob - avg_actual > 0.05,
        "under_confidence_flag": avg_actual - avg_prob > 0.05,
    }


def write_calibration(calibration: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(calibration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path

