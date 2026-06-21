from pathlib import Path

from cnsvintraday.core.context import IntradayContext
from cnsvintraday.reports.connector_report import render_connector_report, write_connector_report


def test_connector_report_contains_required_sections(tmp_path: Path) -> None:
    context = IntradayContext(
        trade_date="20260622",
        next_trade_date="20260623",
        next2_trade_date="20260624",
        ready=True,
        status="PASS",
        allowed_to_run=True,
        file_checks={"snapshot_1min": True},
    )

    html = render_connector_report(context)

    assert "CNSVintraday V1.1 Data Connector Report" in html
    assert "禁止正式信号" in html
    assert "20260623" in html

    output = tmp_path / "docs/reports/20260622/connector_report_1400.html"
    latest = tmp_path / "docs/connector_latest.html"
    write_connector_report(context, output, latest)
    assert output.exists()
    assert latest.exists()
