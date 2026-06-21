from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cnsvintraday.core.context import IntradayContext
from cnsvintraday.data.calendar import TradeCalendar
from cnsvintraday.data.ready_reader import ReadyReader, ready_allows_observation
from cnsvintraday.data.snapshot_reader import SnapshotReader
from cnsvintraday.reports.connector_report import write_connector_report
from cnsvintraday.utils.paths import (
    DEFAULT_CALENDAR_PATH,
    DEFAULT_CONNECTOR_LATEST_PATH,
    DEFAULT_CONTEXT_LATEST_PATH,
    DEFAULT_READY_PATH,
    context_path,
    ensure_parent,
    normalize_trade_date,
    report_path,
)
from cnsvintraday.validation.future_guard import apply_future_guard


def _ready_trade_date(ready_data: dict[str, Any]) -> str | None:
    for key in ("trade_date", "snapshot_trade_date", "latest_trade_date"):
        if ready_data.get(key):
            return normalize_trade_date(ready_data[key])
    latest_snapshot = ready_data.get("latest_snapshot") or {}
    if isinstance(latest_snapshot, dict) and latest_snapshot.get("trade_date"):
        return normalize_trade_date(latest_snapshot["trade_date"])
    return None


def build_context(
    data_root: Path,
    trade_date: str | None = None,
    snapshot_time: str = "1400",
    calendar_path: Path | None = None,
    ready_path: Path | None = None,
    load_minute_frame: bool = False,
) -> IntradayContext:
    data_root = data_root.resolve()
    calendar_path = calendar_path or data_root / DEFAULT_CALENDAR_PATH
    ready_path = ready_path or data_root / DEFAULT_READY_PATH

    ready_data = ReadyReader(ready_path).read()
    selected_trade_date = trade_date or _ready_trade_date(ready_data)
    if not selected_trade_date:
        raise ValueError("trade-date is required when ready file does not include trade_date")
    selected_trade_date = normalize_trade_date(selected_trade_date)

    calendar = TradeCalendar(calendar_path)
    window = calendar.resolve_window(selected_trade_date)
    reader = SnapshotReader(data_root, selected_trade_date, snapshot_time)
    paths = reader.paths

    context = IntradayContext(
        trade_date=window.trade_date,
        next_trade_date=window.next_trade_date,
        next2_trade_date=window.next2_trade_date,
        ts_code=str(ready_data.get("ts_code", "600150.SH")),
        snapshot_time=snapshot_time,
        data_cutoff_time="14:00",
        ready=bool(ready_data.get("ready", False)),
        status=str(ready_data.get("status", "FAIL")).upper(),
        data_root=str(data_root),
        ready_path=str(ready_path),
        calendar_path=str(calendar_path),
        snapshot_1min_path=str(paths["snapshot_1min"]),
        snapshot_5min_path=str(paths["snapshot_5min"]),
        snapshot_15min_path=str(paths["snapshot_15min"]),
        snapshot_json_path=str(paths["snapshot_json"]),
        quality_path=str(paths["quality"]),
        manifest_path=str(paths["manifest"]),
        metadata={"ready": ready_data},
    )

    observation_allowed, warnings, failures = ready_allows_observation(ready_data)
    context.warning_messages.extend(warnings)
    context.fail_reasons.extend(failures)
    context.apply_ready_gate()
    if not observation_allowed:
        context.allowed_to_run = False

    context.file_checks = reader.check_files()
    required_files = {"snapshot_1min", "snapshot_5min", "snapshot_15min", "snapshot_json", "quality", "manifest"}
    for name, exists in context.file_checks.items():
        if not exists and name in required_files:
            context.fail(f"missing {name}")

    frames = []
    if load_minute_frame and context.file_checks.get("snapshot_1min"):
        frames.append(reader.read_minutes("snapshot_1min"))
    apply_future_guard(context, frames)
    context.formal_signal_allowed = False
    return context


def save_context_outputs(context: IntradayContext, data_root: Path) -> tuple[Path, Path]:
    dated_context = context_path(data_root, context.trade_date, context.snapshot_time)
    latest_context = data_root / DEFAULT_CONTEXT_LATEST_PATH
    ensure_parent(dated_context)
    dated_context.write_text(context.to_json() + "\n", encoding="utf-8")
    ensure_parent(latest_context)
    latest_context.write_text(context.to_json() + "\n", encoding="utf-8")

    dated_report = report_path(data_root, context.trade_date, context.snapshot_time)
    latest_report = data_root / DEFAULT_CONNECTOR_LATEST_PATH
    write_connector_report(context, dated_report, latest_report)
    return dated_context, dated_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build CNSVintraday V1.1 IntradayContext")
    parser.add_argument("--data-root", default=".", help="CNSVdata contract root")
    parser.add_argument("--trade-date", default=None, help="T date in YYYYMMDD")
    parser.add_argument("--snapshot-time", default="1400")
    parser.add_argument("--calendar-path", default=None)
    parser.add_argument("--ready-path", default=None)
    parser.add_argument("--load-minute-frame", action="store_true")
    args = parser.parse_args(argv)

    data_root = Path(args.data_root)
    context = build_context(
        data_root=data_root,
        trade_date=args.trade_date,
        snapshot_time=args.snapshot_time,
        calendar_path=Path(args.calendar_path) if args.calendar_path else None,
        ready_path=Path(args.ready_path) if args.ready_path else None,
        load_minute_frame=args.load_minute_frame,
    )
    context_file, report_file = save_context_outputs(context, data_root.resolve())
    summary = {
        "trade_date": context.trade_date,
        "next_trade_date": context.next_trade_date,
        "status": context.status,
        "allowed_to_run": context.allowed_to_run,
        "formal_signal_allowed": False,
        "context_file": str(context_file),
        "report_file": str(report_file),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if context.allowed_to_run else 2


if __name__ == "__main__":
    raise SystemExit(main())
