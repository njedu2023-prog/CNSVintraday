from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cnsvintraday.decision.decision_gate import evaluate_decision_gate
from cnsvintraday.decision.decision_loader import DecisionInputs, load_decision_inputs
from cnsvintraday.decision.decision_report import write_decision_html
from cnsvintraday.decision.decision_summary import build_decision_summary
from cnsvintraday.decision.learning_summary import build_learning_summary
from cnsvintraday.decision.model_summary import build_model_summary
from cnsvintraday.decision.path_summary import build_path_summary
from cnsvintraday.decision.risk_summary import build_risk_summary


def decision_output_paths(data_root: Path, trade_date: str, snapshot_time: str = "1400") -> dict[str, Path]:
    return {
        "html_latest": data_root / "docs" / "decision" / "intraday_decision_latest.html",
        "html_history": data_root / "docs" / "decision" / "reports" / trade_date / f"intraday_decision_{snapshot_time}.html",
        "json_latest": data_root / "data" / "decision" / "intraday_decision_latest.json",
        "json_history": data_root / "data" / "decision" / "history" / trade_date / f"intraday_decision_{snapshot_time}.json",
    }


def assemble_decision_report(inputs: DecisionInputs) -> dict[str, Any]:
    gate = evaluate_decision_gate(inputs)
    model = build_model_summary(inputs.prediction_snapshot, inputs.model_leaderboard)
    path = build_path_summary(inputs.path_distribution)
    learning = build_learning_summary(inputs.learning_state, inputs.learning_metrics)
    risk = build_risk_summary(path, learning, model.get("selected_prediction", {}).get("confidence"), inputs.path_metrics)
    return build_decision_summary(inputs.context, gate, model, path, risk, learning, inputs.missing_files)


def write_decision_outputs(data_root: Path, report: dict[str, Any], output_html: Path | None = None, output_json: Path | None = None) -> dict[str, Path]:
    paths = decision_output_paths(data_root, report["trade_date"], report["snapshot_time"])
    html_latest = output_html or paths["html_latest"]
    json_latest = output_json or paths["json_latest"]
    for json_path in (json_latest, paths["json_history"]):
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for html_path in (html_latest, paths["html_history"]):
        write_decision_html(report, html_path)
    paths["html_latest"] = html_latest
    paths["json_latest"] = json_latest
    return paths


def build_decision_outputs(
    data_root: Path,
    snapshot_time: str = "1400",
    trade_date: str | None = None,
    output_html: Path | None = None,
    output_json: Path | None = None,
) -> dict[str, Any]:
    inputs = load_decision_inputs(data_root, snapshot_time=snapshot_time)
    report = assemble_decision_report(inputs)
    if trade_date:
        report["trade_date"] = trade_date
    paths = write_decision_outputs(Path(data_root), report, output_html=output_html, output_json=output_json)
    return {"report": report, "paths": {key: str(path) for key, path in paths.items()}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build CNSVintraday V2.0 intraday decision report.")
    parser.add_argument("--data-root", default=".")
    parser.add_argument("--trade-date", default=None)
    parser.add_argument("--snapshot-time", default="1400")
    parser.add_argument("--output-html", default=None)
    parser.add_argument("--output-json", default=None)
    args = parser.parse_args(argv)
    build_decision_outputs(
        Path(args.data_root),
        snapshot_time=args.snapshot_time,
        trade_date=args.trade_date,
        output_html=Path(args.output_html) if args.output_html else None,
        output_json=Path(args.output_json) if args.output_json else None,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
