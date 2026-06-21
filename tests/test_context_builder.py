import json
from pathlib import Path

import pandas as pd

from cnsvintraday.data.build_context import build_context, save_context_outputs


def _write_fixture(root: Path, status: str = "PASS") -> None:
    (root / "data/processed").mkdir(parents=True)
    pd.DataFrame(
        [
            {"trade_date": "20260622", "is_open": 1},
            {"trade_date": "20260623", "is_open": 1},
            {"trade_date": "20260624", "is_open": 1},
        ]
    ).to_csv(root / "data/processed/trade_calendar.csv", index=False)
    (root / "metadata/intraday").mkdir(parents=True)
    (root / "metadata/intraday/intraday_ready_1400.json").write_text(
        json.dumps(
            {
                "trade_date": "20260622",
                "ready": status != "FAIL",
                "status": status,
                "allowed_usage": {
                    "can_run_intraday_forecast": True,
                    "can_generate_formal_signal": False,
                },
            }
        ),
        encoding="utf-8",
    )
    base = root / "data/intraday/snapshots/20260622/1400"
    base.mkdir(parents=True)
    for name in [
        "cnsv_1min_asof_1400.parquet",
        "cnsv_5min_asof_1400.parquet",
        "cnsv_15min_asof_1400.parquet",
    ]:
        (base / name).write_bytes(b"placeholder")
    (base / "intraday_quality_1400.json").write_text("{}", encoding="utf-8")
    (base / "intraday_manifest_1400.json").write_text("{}", encoding="utf-8")


def test_context_builder_builds_allowed_context(tmp_path: Path) -> None:
    _write_fixture(tmp_path)

    context = build_context(
        data_root=tmp_path,
        calendar_path=tmp_path / "data/processed/trade_calendar.csv",
    )

    assert context.trade_date == "20260622"
    assert context.next_trade_date == "20260623"
    assert context.allowed_to_run is True
    assert context.formal_signal_allowed is False


def test_context_builder_blocks_fail_status(tmp_path: Path) -> None:
    _write_fixture(tmp_path, status="FAIL")

    context = build_context(
        data_root=tmp_path,
        calendar_path=tmp_path / "data/processed/trade_calendar.csv",
    )

    assert context.allowed_to_run is False
    assert context.status == "FAIL"


def test_context_outputs_are_written(tmp_path: Path) -> None:
    _write_fixture(tmp_path)
    context = build_context(
        data_root=tmp_path,
        calendar_path=tmp_path / "data/processed/trade_calendar.csv",
    )

    context_file, report_file = save_context_outputs(context, tmp_path)

    assert context_file.exists()
    assert report_file.exists()
    assert (tmp_path / "data/runtime/context/intraday_context_latest.json").exists()
    assert (tmp_path / "docs/connector_latest.html").exists()
