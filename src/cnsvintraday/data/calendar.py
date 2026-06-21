from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from cnsvintraday.utils.paths import normalize_trade_date


@dataclass(frozen=True)
class TradeDateWindow:
    trade_date: str
    next_trade_date: str | None
    next2_trade_date: str | None


def _read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"trade calendar not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"unsupported trade calendar format: {path.suffix}")


class TradeCalendar:
    def __init__(self, path: Path):
        self.path = path
        self.frame = _read_table(path)
        self.trade_dates = self._extract_trade_dates(self.frame)

    @staticmethod
    def _extract_trade_dates(frame: pd.DataFrame) -> list[str]:
        date_col = None
        for candidate in ("trade_date", "cal_date", "date"):
            if candidate in frame.columns:
                date_col = candidate
                break
        if date_col is None:
            raise ValueError("trade calendar requires trade_date, cal_date, or date column")

        work = frame.copy()
        if "is_open" in work.columns:
            work = work[work["is_open"].astype(int) == 1]
        elif "open" in work.columns:
            work = work[work["open"].astype(int) == 1]

        dates = sorted({normalize_trade_date(v) for v in work[date_col].dropna().tolist()})
        if not dates:
            raise ValueError("trade calendar has no open trade dates")
        return dates

    def is_trade_date(self, trade_date: str | int) -> bool:
        return normalize_trade_date(trade_date) in set(self.trade_dates)

    def resolve_window(self, trade_date: str | int) -> TradeDateWindow:
        normalized = normalize_trade_date(trade_date)
        if normalized not in self.trade_dates:
            raise ValueError(f"{normalized} is not an A-share trade date")
        idx = self.trade_dates.index(normalized)
        return TradeDateWindow(
            trade_date=normalized,
            next_trade_date=self.trade_dates[idx + 1] if idx + 1 < len(self.trade_dates) else None,
            next2_trade_date=self.trade_dates[idx + 2] if idx + 2 < len(self.trade_dates) else None,
        )
