from __future__ import annotations

import pandas as pd

from cnsvintraday.models.baseline_models import MeanReversionBaselineModel


def test_mean_reversion_model_fades_extended_price() -> None:
    extended = pd.Series({"trade_date": "20260622", "distance_to_vwap": 0.03, "close_position": 0.9})
    discounted = pd.Series({"trade_date": "20260623", "distance_to_vwap": -0.03, "close_position": 0.1})

    model = MeanReversionBaselineModel()

    assert model.predict_one(extended)["prob_up"] < 0.5
    assert model.predict_one(discounted)["prob_up"] > 0.5
