from __future__ import annotations

from cnsvintraday.models.baseline_models import RandomBaselineModel


def test_random_model_outputs_observation_prediction() -> None:
    prediction = RandomBaselineModel().predict_one({"trade_date": "20260622", "next_trade_date": "20260623"})

    assert prediction["model_name"] == "B0"
    assert 0.0 < prediction["prob_up"] < 1.0
    assert prediction["prob_down"] == 1.0 - prediction["prob_up"]
    assert prediction["expected_return"] == 0.0
