from __future__ import annotations

from pathlib import Path


DEFAULT_READY_PATH = Path("metadata/intraday/intraday_ready_1400.json")
DEFAULT_CALENDAR_PATH = Path("data/processed/trade_calendar.parquet")
DEFAULT_CONTEXT_LATEST_PATH = Path("data/runtime/context/intraday_context_latest.json")
DEFAULT_CONNECTOR_LATEST_PATH = Path("docs/connector_latest.html")


def normalize_trade_date(value: str | int) -> str:
    text = str(value).strip()
    if "-" in text:
        return text.replace("-", "")
    return text


def snapshot_dir(data_root: Path, trade_date: str, snapshot_time: str = "1400") -> Path:
    return data_root / "data" / "intraday" / "snapshots" / trade_date / snapshot_time


def context_path(data_root: Path, trade_date: str, snapshot_time: str = "1400") -> Path:
    return data_root / "data" / "runtime" / "context" / trade_date / f"intraday_context_{snapshot_time}.json"


def report_path(data_root: Path, trade_date: str, snapshot_time: str = "1400") -> Path:
    return data_root / "docs" / "reports" / trade_date / f"connector_report_{snapshot_time}.html"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
