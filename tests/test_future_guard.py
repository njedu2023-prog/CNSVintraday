import pandas as pd

from cnsvintraday.core.context import IntradayContext
from cnsvintraday.validation.future_guard import apply_future_guard, check_minute_frame, check_no_future_columns


def test_future_guard_rejects_after_cutoff_time() -> None:
    frame = pd.DataFrame({"trade_time": ["2026-06-22 14:01:00"], "close": [10.0]})

    violations = check_minute_frame(frame)

    assert violations


def test_future_guard_rejects_label_columns() -> None:
    violations = check_no_future_columns(["close", "actual_return_vs_1400"])

    assert violations == ["future/label column is not allowed in context: actual_return_vs_1400"]


def test_apply_future_guard_fails_context() -> None:
    context = IntradayContext(trade_date="20260622", next_trade_date="20260623", next2_trade_date="20260624")
    frame = pd.DataFrame({"feature_time": ["2026-06-22 14:05:00"], "close": [10.0]})

    apply_future_guard(context, [frame])

    assert context.allowed_to_run is False
    assert context.status == "FAIL"
    assert not context.future_guard_passed
