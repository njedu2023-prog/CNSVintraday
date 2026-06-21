from __future__ import annotations

from cnsvintraday.learning.prediction_log import build_prediction_log
from cnsvintraday.learning.truth_joiner import join_prediction_truth

from learning_helpers import make_path_frame, make_prediction_frame, make_truth_frame


def test_truth_joiner_matches_trade_date_and_next_trade_date() -> None:
    log = build_prediction_log(make_prediction_frame(3), make_path_frame(3))

    joined = join_prediction_truth(log, make_truth_frame(3))

    assert joined["joined_status"].eq("JOINED").all()
    assert joined["actual_return_t1"].notna().all()


def test_truth_joiner_marks_pending_when_truth_missing() -> None:
    log = build_prediction_log(make_prediction_frame(2), make_path_frame(2))

    joined = join_prediction_truth(log, None)

    assert joined["joined_status"].eq("PENDING_TRUTH").all()
    assert joined["actual_return_t1"].isna().all()

