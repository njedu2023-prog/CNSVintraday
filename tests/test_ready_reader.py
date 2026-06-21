import json
from pathlib import Path

from cnsvintraday.data.ready_reader import ReadyReader, ready_allows_observation


def test_ready_reader_blocks_false_ready(tmp_path: Path) -> None:
    path = tmp_path / "ready.json"
    path.write_text(json.dumps({"ready": False, "status": "PASS"}), encoding="utf-8")

    data = ReadyReader(path).read()
    allowed, warnings, failures = ready_allows_observation(data)

    assert not allowed
    assert warnings == []
    assert "ready=false" in failures


def test_warn_allows_observation_with_warning() -> None:
    allowed, warnings, failures = ready_allows_observation(
        {"ready": True, "status": "WARN", "allowed_usage": {"can_run_intraday_forecast": True}}
    )

    assert allowed
    assert warnings
    assert failures == []
