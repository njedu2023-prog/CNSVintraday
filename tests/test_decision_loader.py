from __future__ import annotations

from cnsvintraday.decision.decision_loader import load_decision_inputs

from decision_helpers import write_decision_inputs


def test_decision_loader_reads_available_files_and_reports_missing(tmp_path) -> None:
    write_decision_inputs(tmp_path, with_optional=False)

    inputs = load_decision_inputs(tmp_path)

    assert inputs.context is not None
    assert inputs.feature_snapshot is not None
    assert inputs.prediction_snapshot is not None
    assert inputs.path_distribution is not None
    assert any("feature_quality" in item for item in inputs.warning_messages)
