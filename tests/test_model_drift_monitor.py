from __future__ import annotations

from cnsvintraday.learning.model_drift_monitor import build_model_drift


def _metrics(last20_brier: float, last20_rmse: float, last60_brier: float = 0.10, last60_rmse: float = 0.02) -> dict:
    def ok(brier: float, rmse: float) -> dict:
        return {
            "sample_status": "OK",
            "brier_score": brier,
            "rmse": rmse,
            "hit_rate": 0.6,
            "coverage_p10_p90": 0.85,
        }

    return {
        "windows": {
            "last_20": {"overall": ok(last20_brier, last20_rmse)},
            "last_60": {"overall": ok(last60_brier, last60_rmse)},
            "last_150": {"overall": ok(0.10, 0.02)},
        }
    }


def test_model_drift_monitor_detects_degrading() -> None:
    drift = build_model_drift(_metrics(0.15, 0.04))

    assert drift["drift_status"] == "DEGRADING"


def test_model_drift_monitor_detects_improving_or_stable() -> None:
    improving = build_model_drift(_metrics(0.06, 0.01))
    stable = build_model_drift(_metrics(0.105, 0.021))

    assert improving["drift_status"] == "IMPROVING"
    assert stable["drift_status"] == "STABLE"

