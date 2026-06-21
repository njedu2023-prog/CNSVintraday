from __future__ import annotations

from cnsvintraday.decision.path_summary import build_path_summary

from learning_helpers import make_path_frame


def test_path_summary_exposes_p10_p50_p90_prices() -> None:
    summary = build_path_summary(make_path_frame(1))

    assert summary["returns"]["path_p10"] == -0.03
    assert summary["returns"]["path_p50"] == 0.0
    assert summary["returns"]["path_p90"] == 0.03
    assert summary["prices"]["price_p90"] == 103.0
