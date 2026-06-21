from __future__ import annotations

from cnsvintraday.features.strength_features import build_strength_features

from feature_helpers import make_minute_frame


def test_strength_features_flag_intraday_breaks() -> None:
    features = build_strength_features(make_minute_frame())

    assert set(features) == {
        "high_break",
        "low_break",
        "new_high_intraday",
        "new_low_intraday",
        "close_strength",
        "intraday_strength_score",
    }
    assert features["new_high_intraday"] == 1.0
    assert features["new_low_intraday"] == 0.0
