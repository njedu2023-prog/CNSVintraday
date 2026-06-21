from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def write_path_dashboard(distribution: pd.DataFrame, metrics: dict[str, Any], path: Path) -> None:
    latest = distribution.tail(1).iloc[0].to_dict()
    rows = distribution.tail(20).to_dict("records")
    html_rows = "\n".join(
        "<tr>"
        f"<td>{row['trade_date']}</td>"
        f"<td>{row['path_p10']:.4f}</td>"
        f"<td>{row['path_p25']:.4f}</td>"
        f"<td>{row['path_p50']:.4f}</td>"
        f"<td>{row['path_p75']:.4f}</td>"
        f"<td>{row['path_p90']:.4f}</td>"
        f"<td>{row['downside_risk']:.4f}</td>"
        f"<td>{row['upside_potential']:.4f}</td>"
        "</tr>"
        for row in rows
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CNSVintraday V1.4 Path Dashboard</title>
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
  <h1>CNSVintraday V1.4 Path Dashboard</h1>
  <div class="summary">
    <div class="metric"><div class="label">Latest Trade Date</div><div class="value">{latest['trade_date']}</div></div>
    <div class="metric"><div class="label">Coverage</div><div class="value">{metrics['coverage']:.2%}</div></div>
    <div class="metric"><div class="label">Interval Width</div><div class="value">{metrics['interval_width']:.4f}</div></div>
    <div class="metric"><div class="label">RMSE</div><div class="value">{metrics['rmse']:.4f}</div></div>
    <div class="metric"><div class="label">P10</div><div class="value">{latest['path_p10']:.4f}</div></div>
    <div class="metric"><div class="label">P25</div><div class="value">{latest['path_p25']:.4f}</div></div>
    <div class="metric"><div class="label">P50</div><div class="value">{latest['path_p50']:.4f}</div></div>
    <div class="metric"><div class="label">P75</div><div class="value">{latest['path_p75']:.4f}</div></div>
    <div class="metric"><div class="label">P90</div><div class="value">{latest['path_p90']:.4f}</div></div>
    <div class="metric"><div class="label">Recent 20 Coverage</div><div class="value">{metrics['recent_20']['coverage']:.2%}</div></div>
    <div class="metric"><div class="label">Recent 60 Coverage</div><div class="value">{metrics['recent_60']['coverage']:.2%}</div></div>
    <div class="metric"><div class="label">Recent 150 Coverage</div><div class="value">{metrics['recent_150']['coverage']:.2%}</div></div>
  </div>
  <table>
    <thead><tr><th>Trade Date</th><th>P10</th><th>P25</th><th>P50</th><th>P75</th><th>P90</th><th>Downside</th><th>Upside</th></tr></thead>
    <tbody>{html_rows}</tbody>
  </table>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")

