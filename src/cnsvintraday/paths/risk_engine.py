from __future__ import annotations


def build_risk_summary(distribution: dict[str, float]) -> dict[str, float]:
    downside = float(distribution["path_p10"])
    upside = float(distribution["path_p90"])
    width = upside - downside
    return {
        "downside_risk": downside,
        "upside_potential": upside,
        "expected_range": width,
        "volatility_score": max(0.0, min(width / 0.10, 1.0)),
    }

