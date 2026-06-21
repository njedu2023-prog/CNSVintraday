from __future__ import annotations

from cnsvintraday.decision.risk_summary import build_risk_summary


def test_risk_summary_assigns_level() -> None:
    risk = build_risk_summary(
        {"available": True, "downside_risk": -0.04, "upside_potential": 0.04, "expected_range": 0.08},
        {"drift_status": "DEGRADING", "calibration_status": "INSUFFICIENT"},
        confidence=0.1,
        path_metrics={"coverage": 0.7},
    )

    assert risk["risk_level"] == "HIGH"
