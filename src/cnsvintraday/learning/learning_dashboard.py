from __future__ import annotations

from pathlib import Path
from typing import Any


def _metric_cell(metrics: dict[str, Any], window: str, key: str) -> str:
    value = metrics["windows"][window]["overall"].get(key)
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def write_learning_dashboard(state: dict[str, Any], metrics: dict[str, Any], calibration: dict[str, Any], drift: dict[str, Any], path: Path) -> Path:
    rows = "\n".join(
        "<tr>"
        f"<td>{window}</td>"
        f"<td>{_metric_cell(metrics, window, 'sample_status')}</td>"
        f"<td>{_metric_cell(metrics, window, 'sample_count')}</td>"
        f"<td>{_metric_cell(metrics, window, 'brier_score')}</td>"
        f"<td>{_metric_cell(metrics, window, 'rmse')}</td>"
        f"<td>{_metric_cell(metrics, window, 'hit_rate')}</td>"
        f"<td>{_metric_cell(metrics, window, 'coverage_p10_p90')}</td>"
        "</tr>"
        for window in ("latest", "last_20", "last_60", "last_150")
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CNSVintraday V1.5 Learning Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; }}
    h1 {{ font-size: 24px; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 12px; margin: 20px 0; }}
    .metric {{ border: 1px solid #d1d5db; border-radius: 6px; padding: 12px; }}
    .label {{ color: #6b7280; font-size: 12px; }}
    .value {{ font-size: 20px; margin-top: 6px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
    th, td {{ border-bottom: 1px solid #e5e7eb; padding: 8px; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
  </style>
</head>
<body>
  <h1>CNSVintraday V1.5 Learning Dashboard</h1>
  <div class="summary">
    <div class="metric"><div class="label">Latest Prediction Date</div><div class="value">{state['latest_trade_date']}</div></div>
    <div class="metric"><div class="label">Latest Truth Date</div><div class="value">{state['latest_truth_date']}</div></div>
    <div class="metric"><div class="label">Sample Count</div><div class="value">{state['sample_count']}</div></div>
    <div class="metric"><div class="label">System Status</div><div class="value">{state['learning_status']}</div></div>
    <div class="metric"><div class="label">Calibration</div><div class="value">{state['calibration_status']}</div></div>
    <div class="metric"><div class="label">Drift Status</div><div class="value">{drift['drift_status']}</div></div>
    <div class="metric"><div class="label">Best 20</div><div class="value">{state['best_model_last_20']}</div></div>
    <div class="metric"><div class="label">Review Mode</div><div class="value">Observation Only</div></div>
  </div>
  <table>
    <thead><tr><th>Window</th><th>Status</th><th>Samples</th><th>Brier</th><th>RMSE</th><th>Hit Rate</th><th>Coverage</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <p>Operational outputs remain disabled in this layer. Review is limited to validation and learning evidence.</p>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path

