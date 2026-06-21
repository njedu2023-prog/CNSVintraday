from __future__ import annotations

import html
from pathlib import Path
from typing import Any


def _fmt(value: Any, pct: bool = False) -> str:
    if value is None:
        return "NA"
    if isinstance(value, (int, float)):
        return f"{value:.2%}" if pct else f"{value:.4f}"
    return html.escape(str(value))


def _card(title: str, body: str) -> str:
    return f"<section class=\"card\"><h2>{html.escape(title)}</h2>{body}</section>"


def build_decision_html(report: dict[str, Any]) -> str:
    prediction = report["prediction"]
    path = report["path_distribution"]
    risk = report["risk"]
    learning = report["learning_summary"]
    model = report["model_summary"]
    data_quality = report["data_quality"]
    warnings = "".join(f"<li>{html.escape(item)}</li>" for item in report["warning_messages"]) or "<li>None</li>"
    failures = "".join(f"<li>{html.escape(item)}</li>" for item in report["fail_reasons"]) or "<li>None</li>"
    model_rows = "".join(
        f"<tr><td>{html.escape(str(row.get('model_name', '')))}</td><td>{_fmt(row.get('prob_up'), True)}</td><td>{_fmt(row.get('expected_return'), True)}</td><td>{_fmt(row.get('confidence'), True)}</td></tr>"
        for row in model.get("models", [])
    )
    metric_rows = "".join(
        f"<tr><td>{label}</td><td>{html.escape(str(values.get('sample_status', 'NA')))}</td><td>{_fmt(values.get('brier_score'))}</td><td>{_fmt(values.get('rmse'))}</td><td>{_fmt(values.get('hit_rate'), True)}</td><td>{_fmt(values.get('coverage_p10_p90'), True)}</td></tr>"
        for label, values in (("Last 20", learning.get("last_20", {})), ("Last 60", learning.get("last_60", {})), ("Last 150", learning.get("last_150", {})))
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CNSVintraday V2.0 Intraday Decision Report</title>
  <style>
    :root {{ color-scheme: light; --bg:#f5f5f7; --card:#fff; --text:#1d1d1f; --muted:#6e6e73; --line:#d2d2d7; --blue:#0071e3; --red:#b42318; --green:#1d7f3b; --amber:#8a5a00; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",Arial,sans-serif; letter-spacing:0; }}
    main {{ max-width:1180px; margin:0 auto; padding:38px 22px 54px; }}
    .hero {{ display:grid; grid-template-columns:1fr auto; gap:24px; align-items:end; margin-bottom:24px; }}
    h1 {{ font-size:40px; line-height:1.05; margin:0; font-weight:700; }}
    .subtitle {{ color:var(--muted); font-size:17px; margin-top:10px; max-width:760px; }}
    .status {{ border-radius:8px; padding:10px 14px; background:var(--card); border:1px solid var(--line); font-weight:700; color:var(--blue); }}
    .grid {{ display:grid; grid-template-columns:repeat(12,1fr); gap:14px; }}
    .card {{ grid-column:span 4; background:var(--card); border:1px solid #ececf0; border-radius:8px; padding:22px; min-height:160px; box-shadow:0 1px 2px rgba(0,0,0,.03); }}
    .wide {{ grid-column:span 8; }}
    .full {{ grid-column:1/-1; }}
    h2 {{ margin:0 0 14px; font-size:18px; line-height:1.25; }}
    .kpi {{ font-size:34px; font-weight:700; margin:6px 0; }}
    .muted {{ color:var(--muted); font-size:13px; line-height:1.45; }}
    .pair {{ display:flex; justify-content:space-between; gap:16px; border-top:1px solid #ededf0; padding-top:10px; margin-top:10px; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ border-bottom:1px solid #ededf0; padding:10px 6px; text-align:right; }}
    th:first-child,td:first-child {{ text-align:left; }}
    ul {{ margin:0; padding-left:18px; color:var(--muted); line-height:1.55; }}
    .notice {{ background:#fff; border:1px solid var(--line); border-radius:8px; padding:18px 22px; margin-top:14px; color:var(--muted); }}
    @media (max-width: 860px) {{ .hero {{ grid-template-columns:1fr; }} .card,.wide {{ grid-column:1/-1; }} h1 {{ font-size:32px; }} }}
  </style>
</head>
<body>
<main>
  <div class="hero">
    <div>
      <h1>CNSVintraday V2.0 Intraday Decision Report</h1>
      <div class="subtitle">T 日 14:00 后人工观察与辅助分析报告。预测对象为 T+1 交易日。</div>
    </div>
    <div class="status">{html.escape(report['report_status'])}</div>
  </div>
  <div class="grid">
    {_card("Top Status", f"<div class='pair'><span>Trade Date</span><strong>{html.escape(report['trade_date'])}</strong></div><div class='pair'><span>Next Trade Date</span><strong>{html.escape(report['next_trade_date'])}</strong></div><div class='pair'><span>Snapshot</span><strong>{html.escape(report['snapshot_time'])}</strong></div><div class='pair'><span>Observation</span><strong>{report['observation_allowed']}</strong></div><div class='pair'><span>Formal Signal</span><strong>False</strong></div>")}
    {_card("Core Prediction", f"<div class='muted'>T+1 up probability</div><div class='kpi'>{_fmt(prediction.get('prob_up'), True)}</div><div class='pair'><span>Down probability</span><strong>{_fmt(prediction.get('prob_down'), True)}</strong></div><div class='pair'><span>Expected return</span><strong>{_fmt(prediction.get('expected_return'), True)}</strong></div><div class='pair'><span>Confidence</span><strong>{_fmt(prediction.get('confidence'), True)}</strong></div>")}
    {_card("Risk", f"<div class='muted'>Risk level</div><div class='kpi'>{html.escape(str(risk.get('risk_level', 'UNKNOWN')))}</div><div class='pair'><span>Downside</span><strong>{_fmt(risk.get('downside_risk'), True)}</strong></div><div class='pair'><span>Upside</span><strong>{_fmt(risk.get('upside_potential'), True)}</strong></div><div class='pair'><span>Range</span><strong>{_fmt(risk.get('expected_range'), True)}</strong></div>")}
    <section class="card wide"><h2>Path Distribution</h2><table><tr><th>Scenario</th><th>P10</th><th>P50</th><th>P90</th></tr><tr><td>Return</td><td>{_fmt(path.get('path_p10'), True)}</td><td>{_fmt(path.get('path_p50'), True)}</td><td>{_fmt(path.get('path_p90'), True)}</td></tr><tr><td>Price</td><td>{_fmt(path.get('price_p10'))}</td><td>{_fmt(path.get('price_p50'))}</td><td>{_fmt(path.get('price_p90'))}</td></tr></table><p class="muted">P10 表示偏悲观情形，P50 表示中位情形，P90 表示偏乐观情形，不是必然目标价。</p></section>
    <section class="card"><h2>Data Quality</h2><div class='pair'><span>Ready</span><strong>{data_quality.get('ready')}</strong></div><div class='pair'><span>Status</span><strong>{data_quality.get('status')}</strong></div><div class='pair'><span>Future Guard</span><strong>{data_quality.get('future_guard_passed')}</strong></div></section>
    <section class="card wide"><h2>Model Status</h2><div class="muted">Selected model: {html.escape(str(model.get('best_model')))}. {html.escape(str(model.get('model_advantage_note')))}</div><table><tr><th>Model</th><th>Prob Up</th><th>Expected Return</th><th>Confidence</th></tr>{model_rows}</table></section>
    <section class="card"><h2>Learning State</h2><div class='pair'><span>Samples</span><strong>{learning.get('sample_count')}</strong></div><div class='pair'><span>Drift</span><strong>{learning.get('drift_status')}</strong></div><div class='pair'><span>Calibration</span><strong>{learning.get('calibration_status')}</strong></div><p class="muted">{html.escape(str(learning.get('sample_note')))}</p></section>
    <section class="card full"><h2>Learning Metrics</h2><table><tr><th>Window</th><th>Status</th><th>Brier</th><th>RMSE</th><th>Hit Rate</th><th>Coverage</th></tr>{metric_rows}</table></section>
    <section class="card full"><h2>Warnings and Failures</h2><div class="grid"><div class="card"><h2>Warnings</h2><ul>{warnings}</ul></div><div class="card"><h2>Failures</h2><ul>{failures}</ul></div></div></section>
  </div>
  <div class="notice">本报告仅用于 T 日 14:00 后人工观察与辅助分析。本报告不构成正式买入、卖出或持仓建议。</div>
</main>
</body>
</html>
"""


def write_decision_html(report: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_decision_html(report), encoding="utf-8")
    return path
