from __future__ import annotations

import pandas as pd
import pytest

from cnsvintraday.models.labels import build_t1_labels
from cnsvintraday.paths.path_replay import prepare_path_frame
from cnsvintraday.paths.similarity_engine import find_similar_samples, path_feature_columns

from model_helpers import make_feature_frame, make_label_source


def test_similarity_engine_returns_nearest_ranked_samples() -> None:
    features = make_feature_frame(25)
    frame, columns = prepare_path_frame(features, make_label_source(25))
    history = frame.iloc[:20]
    current = frame.iloc[20]

    samples = find_similar_samples(history, current, columns, sample_count=5)

    assert len(samples) == 5
    assert list(samples["similarity_rank"]) == [1, 2, 3, 4, 5]
    assert samples["distance"].is_monotonic_increasing
    assert "label_return_t1" in samples.columns


def test_similarity_engine_blocks_future_feature_columns() -> None:
    frame = make_feature_frame(5)
    frame["next_close_leak"] = 1.0

    with pytest.raises(ValueError, match="future guard failed"):
        path_feature_columns(frame)


def test_prepare_path_frame_keeps_labels_out_of_features() -> None:
    labels = build_t1_labels(make_label_source(5))
    assert {"next_trade_date", "label_return_t1"}.issubset(labels.columns)

    frame, columns = prepare_path_frame(make_feature_frame(5), make_label_source(5))

    assert "label_return_t1" in frame.columns
    assert "label_return_t1" not in columns
    assert "next_trade_date" not in columns

