from __future__ import annotations

import pandas as pd

from cnsvintraday.learning.prediction_log import build_prediction_log, write_prediction_log

from learning_helpers import make_path_frame, make_prediction_frame


def test_prediction_log_writes_latest_and_history(tmp_path) -> None:
    log = build_prediction_log(make_prediction_frame(2), make_path_frame(2), snapshot_time="1400", created_at="2026-01-01T00:00:00Z")

    paths = write_prediction_log(tmp_path, log, snapshot_time="1400")

    assert paths["latest"].is_file()
    assert paths["history"].is_file()
    written = pd.read_parquet(paths["latest"])
    assert {"run_id", "feature_version", "path_version", "formal_signal_allowed"}.issubset(written.columns)
    assert written["formal_signal_allowed"].eq(False).all()

