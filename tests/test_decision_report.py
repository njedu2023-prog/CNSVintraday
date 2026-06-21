from __future__ import annotations

from cnsvintraday.decision.build_decision import assemble_decision_report
from cnsvintraday.decision.decision_loader import load_decision_inputs
from cnsvintraday.decision.decision_report import build_decision_html

from decision_helpers import write_decision_inputs


def test_decision_report_generates_apple_like_html_without_trade_instructions(tmp_path) -> None:
    write_decision_inputs(tmp_path)
    report = assemble_decision_report(load_decision_inputs(tmp_path))

    html = build_decision_html(report)

    assert "CNSVintraday V2.0 Intraday Decision Report" in html
    assert "#f5f5f7" in html
    for forbidden in ("买入信号", "卖出信号", "建仓指令", "清仓指令", "仓位建议", "自动下单"):
        assert forbidden not in html
