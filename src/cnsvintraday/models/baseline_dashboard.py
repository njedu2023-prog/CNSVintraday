from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


def render_baseline_dashboard(leaderboard: dict[str, Any]) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for item in leaderboard.get("models", []):
        rows.append(
            "<tr>"
            f"<td>{escape(str(item['model_name']))}</td>"
            f"<td>{float(item['auc']):.4f}</td>"
            f"<td>{float(item['brier']):.4f}</td>"
            f"<td>{float(item['rmse']):.4f}</td>"
            f"<td>{float(item['hit_rate']):.4f}</td>"
            "</tr>"
        )
    body_rows = "".join(rows)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>CNSVintraday V1.3 Baseline Dashboard</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #1f2937; }}
    h1 {{ font-size: 24px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; }}
    th {{ background: #f3f4f6; }}
  </style>
</head>
<body>
  <h1>CNSVintraday V1.3 Baseline Dashboard</h1>
  <p>Generated At: {escape(generated_at)}</p>
  <table>
    <thead><tr><th>Model</th><th>AUC</th><th>Brier</th><th>RMSE</th><th>Hit Rate</th></tr></thead>
    <tbody>{body_rows}</tbody>
  </table>
  <p>V1.3 outputs observation-level predictions only. No buy signal, sell signal, automatic trading, or formal signal is generated.</p>
</body>
</html>
"""


def write_baseline_dashboard(leaderboard: dict[str, Any], path: Path) -> str:
    html = render_baseline_dashboard(leaderboard)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return html
