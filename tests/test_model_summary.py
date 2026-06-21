from __future__ import annotations

from cnsvintraday.decision.model_summary import build_model_summary

from learning_helpers import make_prediction_frame


def test_model_summary_selects_confident_model_and_compares_b0() -> None:
    summary = build_model_summary(
        make_prediction_frame(1),
        {"models": [{"model_name": "B0", "brier": 0.30}, {"model_name": "B1", "brier": 0.10}]},
    )

    assert summary["best_model"] in {"B0", "B1"}
    assert "models" in summary
    assert summary["model_advantage_note"]
