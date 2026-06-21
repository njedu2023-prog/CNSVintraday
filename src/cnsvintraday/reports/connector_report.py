from __future__ import annotations

from html import escape
from pathlib import Path

from cnsvintraday.core.context import IntradayContext


def _status_class(status: str) -> str:
    status = (status or "FAIL").upper()
    if status == "PASS":
        return "pass"
    if status == "WARN":
        return "warn"
    return "fail"


def render_connector_report(context: IntradayContext) -> str:
    status_class = _status_class(context.status)
    rows = [
        ("当前 T 日", context.trade_date),
        ("目标 T+1 交易日", context.next_trade_date or ""),
        ("目标 T+2 交易日", context.next2_trade_date or ""),
        ("数据截止时间", context.data_cutoff_time),
        ("ready", str(context.ready)),
        ("状态", context.status),
        ("是否允许进入下一阶段", str(context.allowed_to_run)),
        ("未来函数检查", "PASS" if context.future_guard_passed else "FAIL"),
        ("正式信号允许", "False"),
    ]
    file_rows = "".join(
        f"<tr><td>{escape(name)}</td><td>{'YES' if exists else 'NO'}</td></tr>"
        for name, exists in sorted(context.file_checks.items())
    )
    warnings = "".join(f"<li>{escape(item)}</li>" for item in context.warning_messages) or "<li>无</li>"
    failures = "".join(f"<li>{escape(item)}</li>" for item in context.fail_reasons) or "<li>无</li>"
    main_rows = "".join(f"<tr><td>{escape(k)}</td><td>{escape(v)}</td></tr>" for k, v in rows)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>CNSVintraday V1.1 Data Connector Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #1f2937; }}
    h1 {{ font-size: 24px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0 28px; }}
    td, th {{ border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; }}
    th {{ background: #f3f4f6; }}
    .badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-weight: 700; }}
    .pass {{ background: #dcfce7; color: #166534; }}
    .warn {{ background: #fef3c7; color: #92400e; }}
    .fail {{ background: #fee2e2; color: #991b1b; }}
  </style>
</head>
<body>
  <h1>CNSVintraday V1.1 Data Connector Report</h1>
  <p><span class="badge {status_class}">{escape(context.status)}</span></p>
  <h2>接线状态</h2>
  <table><tbody>{main_rows}</tbody></table>
  <h2>文件检查</h2>
  <table><thead><tr><th>文件</th><th>存在</th></tr></thead><tbody>{file_rows}</tbody></table>
  <h2>警告</h2>
  <ul>{warnings}</ul>
  <h2>阻断原因</h2>
  <ul>{failures}</ul>
  <p>本报告仅用于 V1.1 Data Connector 验收。当前阶段禁止正式信号、买卖建议和自动交易。</p>
</body>
</html>
"""


def write_connector_report(context: IntradayContext, path: Path, latest_path: Path | None = None) -> None:
    html = render_connector_report(context)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    if latest_path is not None:
        latest_path.parent.mkdir(parents=True, exist_ok=True)
        latest_path.write_text(html, encoding="utf-8")
