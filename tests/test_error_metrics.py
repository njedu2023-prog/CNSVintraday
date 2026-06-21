from __future__ import annotations

from cnsvintraday.learning.error_metrics import build_learning_metrics
from cnsvintraday.learning.prediction_log import build_prediction_log
from cnsvintraday.learning.truth_joiner import join_prediction_truth

from learning_helpers import make_path_frame, make_prediction_frame, make_truth_frame


def test_error_metrics_compute_brier_rmse_and_coverage() -> None:
    log = build_prediction_log(make_prediction_frame(25), make_path_frame(25))
    joined = join_prediction_truth(log, make_truth_frame(25))

    metrics = build_learning_metrics(joined)
    last_20 = metrics["windows"]["last_20"]["overall"]

    assert last_20["sample_status"] == "OK"
    assert 0.07 < last_20["brier_score"] < 0.15
    assert last_20["rmse"] < 0.01
    assert last_20["coverage_p10_p90"] == 1.0


def test_error_metrics_mark_insufficient_samples() -> None:
    log = build_prediction_log(make_prediction_frame(5), make_path_frame(5))
    joined = join_prediction_truth(log, make_truth_frame(5))

    metrics = build_learning_metrics(joined)

    assert metrics["windows"]["last_20"]["overall"]["sample_status"] == "INSUFFICIENT"

