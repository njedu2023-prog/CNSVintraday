from __future__ import annotations

from cnsvintraday.decision.decision_gate import evaluate_decision_gate
from cnsvintraday.decision.decision_loader import load_decision_inputs

from decision_helpers import write_decision_inputs


def test_decision_gate_core_file_missing_fails(tmp_path) -> None:
    write_decision_inputs(tmp_path)
    (tmp_path / "data" / "models" / "prediction_snapshot_1400.parquet").unlink()

    gate = evaluate_decision_gate(load_decision_inputs(tmp_path))

    assert gate["report_status"] == "FAIL"


def test_decision_gate_optional_file_missing_warns(tmp_path) -> None:
    write_decision_inputs(tmp_path, with_optional=False)

    gate = evaluate_decision_gate(load_decision_inputs(tmp_path))

    assert gate["report_status"] == "WARN"


def test_decision_gate_context_and_signal_failures(tmp_path) -> None:
    write_decision_inputs(tmp_path)
    inputs = load_decision_inputs(tmp_path)
    inputs.context["status"] = "FAIL"
    inputs.context["future_guard_passed"] = False
    inputs.context["formal_signal_allowed"] = True
    inputs.learning_state["allowed_usage"]["can_generate_formal_signal"] = True

    gate = evaluate_decision_gate(inputs)

    assert gate["report_status"] == "FAIL"
    assert "formal_signal_allowed=true" in gate["fail_reasons"]
    assert "can_generate_formal_signal=true" in gate["fail_reasons"]
