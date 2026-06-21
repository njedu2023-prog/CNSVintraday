from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass
class IntradayContext:
    trade_date: str
    next_trade_date: str | None
    next2_trade_date: str | None
    ts_code: str = "600150.SH"
    snapshot_time: str = "1400"
    data_cutoff_time: str = "14:00"
    ready: bool = False
    status: str = "FAIL"
    allowed_to_run: bool = False
    warning_messages: list[str] = field(default_factory=list)
    fail_reasons: list[str] = field(default_factory=list)
    data_root: str = "."
    ready_path: str = ""
    calendar_path: str = ""
    snapshot_1min_path: str = ""
    snapshot_5min_path: str = ""
    snapshot_15min_path: str = ""
    snapshot_json_path: str = ""
    quality_path: str = ""
    manifest_path: str = ""
    model_allowed: bool = False
    formal_signal_allowed: bool = False
    file_checks: dict[str, bool] = field(default_factory=dict)
    future_guard_passed: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def apply_ready_gate(self) -> None:
        self.status = (self.status or "FAIL").upper()
        self.formal_signal_allowed = False
        self.model_allowed = False

        if not self.ready:
            self.allowed_to_run = False
            self._add_fail("ready=false")
            return

        if self.status == "PASS":
            self.allowed_to_run = True
        elif self.status == "WARN":
            self.allowed_to_run = True
            self._add_warning("ready status is WARN; observation run only")
        else:
            self.allowed_to_run = False
            self._add_fail(f"status={self.status}")

    def fail(self, reason: str) -> None:
        self.status = "FAIL"
        self.allowed_to_run = False
        self.future_guard_passed = False
        self._add_fail(reason)

    def _add_warning(self, message: str) -> None:
        if message not in self.warning_messages:
            self.warning_messages.append(message)

    def _add_fail(self, reason: str) -> None:
        if reason not in self.fail_reasons:
            self.fail_reasons.append(reason)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["formal_signal_allowed"] = False
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)

    def save_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json() + "\n", encoding="utf-8")
