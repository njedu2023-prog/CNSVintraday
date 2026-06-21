from __future__ import annotations

import pytest

from cnsvintraday.features.feature_manifest import feature_names
from cnsvintraday.models.baseline_models import LogisticRegressionBaselineModel
from cnsvintraday.models.labels import build_t1_labels
from cnsvintraday.models.replay_engine import prepare_model_frame

from model_helpers import make_feature_frame, make_label_source


def test_logistic_model_requires_training_history() -> None:
    features = make_feature_frame(20)
    labels = build_t1_labels(make_label_source(20))
    frame, columns = prepare_model_frame(features, labels)

    with pytest.raises(ValueError, match="history insufficient"):
        LogisticRegressionBaselineModel().fit(frame, columns)


def test_logistic_model_trains_with_v12_features() -> None:
    features = make_feature_frame(150)
    labels = build_t1_labels(make_label_source(150))
    frame, columns = prepare_model_frame(features, labels)

    model = LogisticRegressionBaselineModel()
    model.fit(frame, columns)
    prediction = model.predict_one(frame.iloc[-1])

    assert set(feature_names()) == set(columns)
    assert prediction["model_name"] == "B3"
    assert 0.0 < prediction["prob_up"] < 1.0
