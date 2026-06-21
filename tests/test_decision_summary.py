from __future__ import annotations

from cnsvintraday.decision.build_decision import assemble_decision_report
from cnsvintraday.decision.decision_loader import load_decision_inputs

from decision_helpers import write_decision_inputs


def test_decision_summary_contains_core_fields(tmp_path) -> None:
    write_decision_inputs(tmp_path)

    report = assemble_decision_report(load_decision_inputs(tmp_path))

    assert report["version"] == "V2.0"
    assert report["formal_signal_allowed"] is False
    assert {"prob_up", "expected_return", "confidence"}.issubset(report["prediction"])
