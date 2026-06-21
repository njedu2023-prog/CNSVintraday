from __future__ import annotations

import pandas as pd

from cnsvintraday.paths.path_distribution import PATH_QUANTILES, build_path_distribution


def test_path_distribution_outputs_required_quantiles() -> None:
    samples = pd.DataFrame({"label_return_t1": [-0.03, -0.01, 0.00, 0.02, 0.05]})

    distribution = build_path_distribution(samples)

    assert set(distribution) == {name for name, _ in PATH_QUANTILES}
    assert distribution["path_p10"] <= distribution["path_p25"] <= distribution["path_p50"]
    assert distribution["path_p50"] <= distribution["path_p75"] <= distribution["path_p90"]

