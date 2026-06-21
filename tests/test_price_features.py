from __future__ import annotations

from cnsvintraday.features.price_features import build_price_features

from feature_helpers import make_minute_frame


def test_price_features_are_intraday_only() -> None:
    features = build_price_features(make_minute_frame())

    assert set(features) == {
        "return_1m",
        "return_5m",
        "return_15m",
        "return_30m",
        "return_60m",
        "high_to_close",
        "low_to_close",
        "open_to_close",
        "day_range_pct",
        "close_position",
    }
    assert features["return_1m"] > 0
    assert 0 <= features["close_position"] <= 1
