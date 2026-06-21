import pandas as pd

from cnsvintraday.validation.future_guard import FUTURE_FIELD_BLACKLIST, check_no_future_columns


def test_future_field_blacklist_blocks_known_future_columns() -> None:
    future_columns = [
        "next_trade_date",
        "t1_return",
        "t+1_signal",
        "future_price",
        "actual_return_vs_1400",
        "realized_volatility",
        "return_next",
        "next_close",
        "next_open",
        "next_high",
        "next_low",
    ]

    violations = check_no_future_columns(future_columns)

    assert len(violations) == len(future_columns)


def test_future_field_blacklist_all_entries_are_effective() -> None:
    columns = [f"feature_{keyword}_value" for keyword in FUTURE_FIELD_BLACKLIST]

    violations = check_no_future_columns(columns)

    assert len(violations) == len(FUTURE_FIELD_BLACKLIST)


def test_future_field_blacklist_allows_intraday_safe_columns() -> None:
    frame = pd.DataFrame(
        {
            "trade_time": ["2026-06-22 14:00:00"],
            "return_from_open_to_1400": [0.01],
            "volume_until_1400": [1000],
        }
    )

    assert check_no_future_columns(frame.columns) == []
