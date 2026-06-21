from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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


def ready_allows_observation(ready_data: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    warnings: list[str] = []
    failures: list[str] = []
    ready = bool(ready_data.get("ready", False))
    status = str(ready_data.get("status", "FAIL")).upper()
    allowed_usage = ready_data.get("allowed_usage") or {}

    if not ready:
        failures.append("ready=false")
    if status == "WARN":
        warnings.append("ready status is WARN")
    elif status != "PASS":
        failures.append(f"status={status}")
    if allowed_usage.get("can_run_intraday_forecast") is False:
        failures.append("allowed_usage.can_run_intraday_forecast=false")
    if allowed_usage.get("can_generate_formal_signal") is True:
        warnings.append("formal signal flag is true upstream; CNSVintraday will force it false")
    return len(failures) == 0, warnings, failures
