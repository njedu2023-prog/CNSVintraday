from __future__ import annotations

from cnsvintraday.learning.calibration_tracker import build_calibration
from cnsvintraday.learning.error_metrics import build_learning_metrics
from cnsvintraday.learning.learning_state import build_learning_state
from cnsvintraday.learning.model_drift_monitor import build_model_drift
from cnsvintraday.learning.prediction_log import build_prediction_log
from cnsvintraday.learning.truth_joiner import join_prediction_truth

from learning_helpers import make_path_frame, make_prediction_frame, make_truth_frame


def test_learning_state_blocks_formal_signal_generation() -> None:
    joined = join_prediction_truth(build_prediction_log(make_prediction_frame(25), make_path_frame(25)), make_truth_frame(25))
    metrics = build_learning_metrics(joined)
    calibration = build_calibration(joined)
    drift = build_model_drift(metrics)

    state = build_learning_state(joined, metrics, calibration, drift)

    assert state["allowed_usage"]["can_generate_formal_signal"] is False
    assert state["allowed_usage"]["can_promote_model"] is False
    assert state["learning_ready"] is True

