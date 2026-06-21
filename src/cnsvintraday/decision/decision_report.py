from __future__ import annotations

import html
from pathlib import Path
from typing import Any


def _fmt(value: Any, pct: bool = False) -> str:
    if value is None:
        return "暂无"
    if isinstance(value, (int, float)):
        return f"{value:.2%}" if pct else f"{value:.4f}"
    return html.escape(str(value))


def _yes_no(value: Any) -> str:
    if isinstance(value, bool):
        return "是" if value else "否"
    return html.escape(str(value))


def _status_text(value: Any) -> str:
    if value is None:
        return "暂无"
    raw = str(value)
    labels = {
        "PASS": "通过",
        "WARN": "警告",
        "FAIL": "失败",
        "READY": "就绪",
        "OK": "正常",
        "MISSING": "缺失",
        "INSUFFICIENT": "样本不足",
        "DEGRADING": "退化",
    }
    return f"{labels.get(raw.upper(), raw)}（{html.escape(raw)}）"


def _risk_text(value: Any) -> str:
    raw = str(value)
    labels = {"LOW": "低", "MEDIUM": "中等", "HIGH": "高", "UNKNOWN": "未知"}
    return f"{labels.get(raw.upper(), raw)}（{html.escape(raw)}）"


def _card(title: str, body: str) -> str:
    return f"<section class=\"card\"><h2>{html.escape(title)}</h2>{body}</section>"


def build_decision_html(report: dict[str, Any]) -> str:
    prediction = report["prediction"]
    path = report["path_distribution"]
    risk = report["risk"]
    learning = report["learning_summary"]
    model = report["model_summary"]
    data_quality = report["data_quality"]
    warnings = "".join(f"<li>{html.escape(item)}</li>" for item in report["warning_messages"]) or "<li>无</li>"
    failures = "".join(f"<li>{html.escape(item)}</li>" for item in report["fail_reasons"]) or "<li>无</li>"
    model_rows = "".join(
        f"<tr><td>{html.escape(str(row.get('model_name', '')))}</td><td>{_fmt(row.get('prob_up'), True)}</td><td>{_fmt(row.get('expected_return'), True)}</td><td>{_fmt(row.get('confidence'), True)}</td></tr>"
        for row in model.get("models", [])
    )
    metric_rows = "".join(
        f"<tr><td>{label}</td><td>{_status_text(values.get('sample_status', '暂无'))}</td><td>{_fmt(values.get('brier_score'))}</td><td>{_fmt(values.get('rmse'))}</td><td>{_fmt(values.get('hit_rate'), True)}</td><td>{_fmt(values.get('coverage_p10_p90'), True)}</td></tr>"
        for label, values in (("最近 20 个样本", learning.get("last_20", {})), ("最近 60 个样本", learning.get("last_60", {})), ("最近 150 个样本", learning.get("last_150", {})))
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CNSVintraday V2.0 盘中决策观察报告</title>
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
      <h1>CNSVintraday V2.0 盘中决策观察报告</h1>
      <div class="subtitle">T 日 14:00 后人工观察与辅助分析报告。预测对象为 T+1 交易日。</div>
    </div>
    <div class="status">{_status_text(report['report_status'])}</div>
  </div>
  <div class="grid">
    {_card("总体状态", f"<div class='pair'><span>交易日</span><strong>{html.escape(report['trade_date'])}</strong></div><div class='pair'><span>下一交易日</span><strong>{html.escape(report['next_trade_date'])}</strong></div><div class='pair'><span>快照时间</span><strong>{html.escape(report['snapshot_time'])}</strong></div><div class='pair'><span>允许观察</span><strong>{_yes_no(report['observation_allowed'])}</strong></div><div class='pair'><span>正式信号</span><strong>否</strong></div>")}
    {_card("核心预测", f"<div class='muted'>T+1 上涨概率</div><div class='kpi'>{_fmt(prediction.get('prob_up'), True)}</div><div class='pair'><span>下跌概率</span><strong>{_fmt(prediction.get('prob_down'), True)}</strong></div><div class='pair'><span>预期收益</span><strong>{_fmt(prediction.get('expected_return'), True)}</strong></div><div class='pair'><span>置信度</span><strong>{_fmt(prediction.get('confidence'), True)}</strong></div>")}
    {_card("风险概览", f"<div class='muted'>风险等级</div><div class='kpi'>{_risk_text(risk.get('risk_level', 'UNKNOWN'))}</div><div class='pair'><span>下行风险</span><strong>{_fmt(risk.get('downside_risk'), True)}</strong></div><div class='pair'><span>上行空间</span><strong>{_fmt(risk.get('upside_potential'), True)}</strong></div><div class='pair'><span>预期波动区间</span><strong>{_fmt(risk.get('expected_range'), True)}</strong></div>")}
    <section class="card wide"><h2>路径分布</h2><table><tr><th>情形</th><th>P10</th><th>P50</th><th>P90</th></tr><tr><td>收益率</td><td>{_fmt(path.get('path_p10'), True)}</td><td>{_fmt(path.get('path_p50'), True)}</td><td>{_fmt(path.get('path_p90'), True)}</td></tr><tr><td>价格</td><td>{_fmt(path.get('price_p10'))}</td><td>{_fmt(path.get('price_p50'))}</td><td>{_fmt(path.get('price_p90'))}</td></tr></table><p class="muted">P10 表示偏悲观情形，P50 表示中位情形，P90 表示偏乐观情形，不是必然目标价。</p></section>
    <section class="card"><h2>数据质量</h2><div class='pair'><span>Ready</span><strong>{_yes_no(data_quality.get('ready'))}</strong></div><div class='pair'><span>Status</span><strong>{_status_text(data_quality.get('status'))}</strong></div><div class='pair'><span>Future Guard</span><strong>{_yes_no(data_quality.get('future_guard_passed'))}</strong></div></section>
    <section class="card wide"><h2>模型状态</h2><div class="muted">选中模型：{html.escape(str(model.get('best_model')))}。{html.escape(str(model.get('model_advantage_note')))}</div><table><tr><th>模型</th><th>上涨概率</th><th>预期收益</th><th>置信度</th></tr>{model_rows}</table></section>
    <section class="card"><h2>自学习状态</h2><div class='pair'><span>样本数</span><strong>{learning.get('sample_count')}</strong></div><div class='pair'><span>漂移状态</span><strong>{_status_text(learning.get('drift_status'))}</strong></div><div class='pair'><span>校准状态</span><strong>{_status_text(learning.get('calibration_status'))}</strong></div><p class="muted">{html.escape(str(learning.get('sample_note')))}</p></section>
    <section class="card full"><h2>自学习指标</h2><table><tr><th>窗口</th><th>状态</th><th>Brier</th><th>RMSE</th><th>命中率</th><th>覆盖率</th></tr>{metric_rows}</table></section>
    <section class="card full"><h2>提示与失败原因</h2><div class="grid"><div class="card"><h2>提示</h2><ul>{warnings}</ul></div><div class="card"><h2>失败原因</h2><ul>{failures}</ul></div></div></section>
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
