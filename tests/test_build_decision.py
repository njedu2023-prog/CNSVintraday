from __future__ import annotations

import json

from cnsvintraday.decision.build_decision import build_decision_outputs, main

from decision_helpers import write_decision_inputs


def test_build_decision_writes_latest_and_history_outputs(tmp_path) -> None:
    write_decision_inputs(tmp_path)

    result = build_decision_outputs(tmp_path)

    paths = result["paths"]
    assert result["report"]["formal_signal_allowed"] is False
    assert (tmp_path / "docs" / "decision" / "intraday_decision_latest.html").is_file()
    assert (tmp_path / "data" / "decision" / "intraday_decision_latest.json").is_file()
    assert "html_history" in paths
    report = json.loads((tmp_path / "data" / "decision" / "intraday_decision_latest.json").read_text(encoding="utf-8"))
    assert report["path_distribution"]["path_p10"] == -0.03


def test_build_decision_cli_runs(tmp_path) -> None:
    write_decision_inputs(tmp_path)

    exit_code = main(["--data-root", str(tmp_path), "--snapshot-time", "1400"])

    assert exit_code == 0
    assert (tmp_path / "docs" / "decision" / "intraday_decision_latest.html").is_file()
