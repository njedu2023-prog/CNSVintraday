from __future__ import annotations

from typing import Any


def build_risk_summary(path_summary: dict[str, Any], learning_summary: dict[str, Any], confidence: float | None, path_metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path_summary.get("available"):
        return {"risk_level": "UNKNOWN", "risk_notes": ["路径分布缺失。"]}
    downside = float(path_summary.get("downside_risk", 0.0))
    expected_range = float(path_summary.get("expected_range", 0.0))
    coverage = None
    if path_metrics:
        coverage = path_metrics.get("coverage")
    risk_score = 0
    if downside <= -0.03:
        risk_score += 1
    if expected_range >= 0.06:
        risk_score += 1
    if learning_summary.get("drift_status") == "DEGRADING":
        risk_score += 1
    if learning_summary.get("calibration_status") == "INSUFFICIENT":
        risk_score += 1
    if confidence is not None and confidence < 0.25:
        risk_score += 1
    if coverage is not None and float(coverage) < 0.8:
        risk_score += 1

    level = "LOW" if risk_score == 0 else "MEDIUM" if risk_score <= 2 else "HIGH"
    return {
        "risk_level": level,
        "downside_risk": downside,
        "upside_potential": float(path_summary.get("upside_potential", 0.0)),
        "expected_range": expected_range,
        "path_coverage": coverage,
        "risk_notes": [
            "高风险不代表价格必然下跌。",
            "低风险不代表价格必然上涨。",
        ],
    }
