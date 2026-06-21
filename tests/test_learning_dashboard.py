from __future__ import annotations

from cnsvintraday.learning.calibration_tracker import build_calibration
from cnsvintraday.learning.error_metrics import build_learning_metrics
from cnsvintraday.learning.learning_dashboard import write_learning_dashboard
from cnsvintraday.learning.learning_state import build_learning_state
from cnsvintraday.learning.model_drift_monitor import build_model_drift
from cnsvintraday.learning.prediction_log import build_prediction_log
from cnsvintraday.learning.truth_joiner import join_prediction_truth

from learning_helpers import make_path_frame, make_prediction_frame, make_truth_frame


def test_learning_dashboard_generates_html_without_action_language(tmp_path) -> None:
    joined = join_prediction_truth(build_prediction_log(make_prediction_frame(25), make_path_frame(25)), make_truth_frame(25))
    metrics = build_learning_metrics(joined)
    calibration = build_calibration(joined)
    drift = build_model_drift(metrics)
    state = build_learning_state(joined, metrics, calibration, drift)

    path = write_learning_dashboard(state, metrics, calibration, drift, tmp_path / "docs" / "learning" / "learning_dashboard.html")
    html = path.read_text(encoding="utf-8")

    assert "CNSVintraday V1.5 Learning Dashboard" in html
    for forbidden in ("买入", "卖出", "建仓", "清仓", "仓位", "正式信号"):
        assert forbidden not in html

