from __future__ import annotations

from cnsvintraday.features.vwap_features import build_vwap_features

from feature_helpers import make_minute_frame


def test_vwap_features_measure_distance_and_trend() -> None:
    features = build_vwap_features(make_minute_frame())

    assert set(features) == {"vwap", "distance_to_vwap", "price_above_vwap", "vwap_trend"}
    assert features["vwap"] > 0
    assert features["price_above_vwap"] == 1.0
