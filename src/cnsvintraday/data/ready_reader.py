from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_READY_FIELDS = ("trade_date", "ready", "status", "allowed_usage")


class ReadyReader:
    def __init__(self, path: Path):
        self.path = path

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(f"ready file not found: {self.path}")
        with self.path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("ready file must be a JSON object")
        return data


def validate_ready_schema(ready_data: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for field in REQUIRED_READY_FIELDS:
        if field not in ready_data:
            failures.append(f"missing required ready field: {field}")

    allowed_usage = ready_data.get("allowed_usage")
    if "allowed_usage" in ready_data and not isinstance(allowed_usage, dict):
        failures.append("allowed_usage must be an object")

    return failures


def ready_allows_observation(ready_data: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    warnings: list[str] = []
    failures: list[str] = validate_ready_schema(ready_data)
    ready = bool(ready_data.get("ready", False))
    status = str(ready_data.get("status", "FAIL")).upper()
    allowed_usage = ready_data.get("allowed_usage") or {}

    if not isinstance(allowed_usage, dict):
        allowed_usage = {}

    if "ready" in ready_data and not ready:
        failures.append("ready=false")
    if "status" in ready_data and status == "WARN":
        warnings.append("ready status is WARN")
    elif "status" in ready_data and status != "PASS":
        failures.append(f"status={status}")
    if allowed_usage.get("can_run_intraday_forecast") is False:
        failures.append("allowed_usage.can_run_intraday_forecast=false")
    if allowed_usage.get("can_generate_formal_signal") is True:
        warnings.append("formal signal flag is true upstream; CNSVintraday will force it false")
    return len(failures) == 0, warnings, failures
