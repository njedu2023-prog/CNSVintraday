from __future__ import annotations

from cnsvintraday.decision.learning_summary import build_learning_summary


def test_learning_summary_marks_missing_and_insufficient() -> None:
    missing = build_learning_summary(None, None)
    insufficient = build_learning_summary({"sample_count": 2, "learning_status": "READY"}, {"windows": {}})

    assert missing["learning_status"] == "Learning State Missing"
    assert "样本不足" in insufficient["sample_note"]
