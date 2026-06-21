from pathlib import Path

import pandas as pd
import pytest

from cnsvintraday.data.calendar import TradeCalendar


def test_trade_calendar_skips_non_open_days(tmp_path: Path) -> None:
    path = tmp_path / "calendar.csv"
    pd.DataFrame(
        [
            {"trade_date": "20260619", "is_open": 1},
            {"trade_date": "20260620", "is_open": 0},
            {"trade_date": "20260621", "is_open": 0},
            {"trade_date": "20260622", "is_open": 1},
            {"trade_date": "20260623", "is_open": 1},
        ]
    ).to_csv(path, index=False)

    window = TradeCalendar(path).resolve_window("20260619")

    assert window.trade_date == "20260619"
    assert window.next_trade_date == "20260622"
    assert window.next2_trade_date == "20260623"


def test_trade_calendar_rejects_non_trade_date(tmp_path: Path) -> None:
    path = tmp_path / "calendar.csv"
    pd.DataFrame([{"trade_date": "20260619", "is_open": 1}]).to_csv(path, index=False)

    with pytest.raises(ValueError):
        TradeCalendar(path).resolve_window("20260620")
