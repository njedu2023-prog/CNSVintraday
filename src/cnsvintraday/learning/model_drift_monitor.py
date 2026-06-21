from __future__ import annotations

import json
from pathlib import Path
from typing import Any


COMPARISONS = (("last_20", "last_60"), ("last_20", "last_150"), ("last_60", "last_150"))


def _overall(metrics: dict[str, Any], window: str) -> dict[str, Any]:
    return metrics["windows"][window]["overall"]


def _compare(short: dict[str, Any], long: dict[str, Any]) -> str:
    if short.get("sample_status") != "OK" or long.get("sample_status") != "OK":
        return "INSUFFICIENT"
    brier_delta = float(short["brier_score"]) - float(long["brier_score"])
    rmse_delta = float(short["rmse"]) - float(long["rmse"])
    coverage_delta = abs(float(short["coverage_p10_p90"]) - float(long["coverage_p10_p90"]))
    if brier_delta > 0.02 and rmse_delta > 0.005:
        return "DEGRADING"
    if brier_delta < -0.02 and rmse_delta < -0.005 and coverage_delta <= 0.15:
        return "IMPROVING"
    return "STABLE"


def build_model_drift(metrics: dict[str, Any]) -> dict[str, Any]:
    comparisons = []
    statuses = []
    for left, right in COMPARISONS:
        status = _compare(_overall(metrics, left), _overall(metrics, right))
        statuses.append(status)
        comparisons.append({"comparison": f"{left}_vs_{right}", "drift_status": status})
    if "DEGRADING" in statuses:
        overall = "DEGRADING"
    elif "IMPROVING" in statuses:
        overall = "IMPROVING"
    elif all(status == "INSUFFICIENT" for status in statuses):
        overall = "INSUFFICIENT"
    elif "INSUFFICIENT" in statuses:
        overall = "INSUFFICIENT"
    else:
        overall = "STABLE"
    return {"drift_status": overall, "comparisons": comparisons}


def write_model_drift(drift: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(drift, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path

