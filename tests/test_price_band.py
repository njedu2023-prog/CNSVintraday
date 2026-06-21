from __future__ import annotations

from cnsvintraday.paths.price_band import build_price_band


def test_price_band_converts_returns_to_prices() -> None:
    band = build_price_band(
        100.0,
        {
            "path_p10": -0.05,
            "path_p25": -0.02,
            "path_p50": 0.01,
            "path_p75": 0.03,
            "path_p90": 0.06,
        },
    )

    assert band["price_p10"] == 95.0
    assert band["price_p50"] == 101.0
    assert band["price_p90"] == 106.0

