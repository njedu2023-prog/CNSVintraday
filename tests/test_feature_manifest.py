from __future__ import annotations

from cnsvintraday.features import FEATURE_VERSION
from cnsvintraday.features.feature_manifest import build_feature_manifest, feature_names


def test_feature_manifest_has_v12_feature_contract() -> None:
    manifest = build_feature_manifest()

    assert manifest["feature_version"] == FEATURE_VERSION
    assert manifest["feature_count"] == len(feature_names())
    assert 30 <= manifest["feature_count"] <= 50
    assert len(feature_names()) == len(set(feature_names()))
    assert "return_next" not in feature_names()
