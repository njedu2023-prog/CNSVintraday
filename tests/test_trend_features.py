from __future__ import annotations

from cnsvintraday.features.trend_features import build_trend_features

from feature_helpers import make_minute_frame


def test_trend_features_include_moving_average_state() -> None:
    features = build_trend_features(make_minute_frame())

    assert set(features) == {
        "ma5",
        "ma10",
        "ma20",
        "price_above_ma5",
        "price_above_ma10",
        "price_above_ma20",
        "ma5_slope",
        "ma10_slope",
        "ma20_slope",
    }
    assert features["price_above_ma20"] == 1.0
    assert features["ma5_slope"] > 0
