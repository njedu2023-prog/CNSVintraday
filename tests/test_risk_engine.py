from __future__ import annotations

from cnsvintraday.paths.risk_engine import build_risk_summary


def test_risk_engine_uses_path_tails() -> None:
    risk = build_risk_summary({"path_p10": -0.04, "path_p90": 0.07})

    assert risk["downside_risk"] == -0.04
    assert risk["upside_potential"] == 0.07
    assert risk["expected_range"] == 0.11000000000000001
    assert risk["volatility_score"] == 1.0

