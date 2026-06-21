from __future__ import annotations

import pandas as pd

from cnsvintraday.models.baseline_models import PersistenceBaselineModel


def test_persistence_model_uses_intraday_momentum() -> None:
    positive = pd.Series({"trade_date": "20260622", "return_15m": 0.01, "return_30m": 0.01, "return_60m": 0.01})
    negative = pd.Series({"trade_date": "20260623", "return_15m": -0.01, "return_30m": -0.01, "return_60m": -0.01})

    model = PersistenceBaselineModel()

    assert model.predict_one(positive)["prob_up"] > 0.5
    assert model.predict_one(negative)["prob_up"] < 0.5
