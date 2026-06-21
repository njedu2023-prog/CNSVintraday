from __future__ import annotations

from cnsvintraday.learning.calibration_tracker import build_calibration
from cnsvintraday.learning.prediction_log import build_prediction_log
from cnsvintraday.learning.truth_joiner import join_prediction_truth

from learning_helpers import make_path_frame, make_prediction_frame, make_truth_frame


def test_calibration_tracker_builds_ten_bins() -> None:
    log = build_prediction_log(make_prediction_frame(20), make_path_frame(20))
    joined = join_prediction_truth(log, make_truth_frame(20))

    calibration = build_calibration(joined)

    assert calibration["sample_status"] == "OK"
    assert len(calibration["calibration_bins"]) == 10
    assert calibration["calibration_error"] is not None


def test_calibration_tracker_marks_insufficient() -> None:
    log = build_prediction_log(make_prediction_frame(2), make_path_frame(2))
    joined = join_prediction_truth(log, make_truth_frame(2))

    calibration = build_calibration(joined, min_samples=20)

    assert calibration["sample_status"] == "INSUFFICIENT"

