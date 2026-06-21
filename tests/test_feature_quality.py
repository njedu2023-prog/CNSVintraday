from __future__ import annotations

import pandas as pd

from cnsvintraday.features.feature_quality import check_feature_quality


def test_feature_quality_passes_clean_snapshot() -> None:
    frame = pd.DataFrame(
        [
            {
                "trade_date": "20260622",
                "snapshot_time": "1400",
                "ts_code": "600150.SH",
                "return_1m": 0.01,
                "volume_1m": 1000,
            }
        ]
    )

    quality = check_feature_quality(frame)

    assert quality["status"] == "PASS"
    assert quality["feature_count"] == 2


def test_feature_quality_fails_future_fields() -> None:
    frame = pd.DataFrame(
        [
            {
                "trade_date": "20260622",
                "snapshot_time": "1400",
                "ts_code": "600150.SH",
                "next_close": 12.3,
            }
        ]
    )

    quality = check_feature_quality(frame)

    assert quality["status"] == "FAIL"
    assert quality["future_violations"]
