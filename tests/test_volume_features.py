from __future__ import annotations

from cnsvintraday.features.volume_features import build_volume_features

from feature_helpers import make_minute_frame


def test_volume_features_cover_ratio_and_acceleration() -> None:
    features = build_volume_features(make_minute_frame())

    assert set(features) == {
        "volume_1m",
        "volume_5m",
        "volume_15m",
        "volume_ratio_5m",
        "volume_ratio_15m",
        "volume_ratio_30m",
        "volume_acceleration",
        "turnover_ratio",
    }
    assert features["volume_15m"] > features["volume_5m"]
    assert features["turnover_ratio"] > 0
