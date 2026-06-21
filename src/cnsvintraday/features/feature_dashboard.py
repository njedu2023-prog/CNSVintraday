from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


def render_feature_dashboard(manifest: dict[str, Any], quality: dict[str, Any]) -> str:
    feature_count = str(manifest.get("feature_count", 0))
    feature_version = str(manifest.get("feature_version", "unknown"))
    status = str(quality.get("status", "FAIL"))
    missing_rates = quality.get("missing_rates", {}) or {}
    missing_avg = 0.0
    if missing_rates:
        missing_avg = sum(float(v) for v in missing_rates.values()) / len(missing_rates)
    abnormal_count = len(quality.get("inf_columns", [])) + len(quality.get("future_violations", []))
    generated_at = datetime.now(timezone.utc).isoformat()
    rows = [
        ("Feature Version", feature_version),
        ("Feature Count", feature_count),
        ("Quality Status", status),
        ("Missing Rate Avg", f"{missing_avg:.4f}"),
        ("Abnormal Count", str(abnormal_count)),
        ("Latest Generated At", generated_at),
    ]
    body_rows = "".join(f"<tr><td>{escape(k)}</td><td>{escape(v)}</td></tr>" for k, v in rows)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>CNSVintraday V1.2 Feature Dashboard</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #1f2937; }}
    h1 {{ font-size: 24px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    td, th {{ border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; }}
    th {{ background: #f3f4f6; }}
  </style>
</head>
<body>
  <h1>CNSVintraday V1.2 Feature Dashboard</h1>
  <h2>Contract Summary</h2>
  <table><tbody>{body_rows}</tbody></table>
  <p>V1.2 只生成特征，不生成预测、概率、买卖建议或正式信号。</p>
</body>
</html>
"""


def write_feature_dashboard(manifest: dict[str, Any], quality: dict[str, Any], path: Path) -> str:
    html = render_feature_dashboard(manifest, quality)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return html
