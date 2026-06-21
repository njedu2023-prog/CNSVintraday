from __future__ import annotations

import numpy as np
import pandas as pd


PATH_QUANTILES: tuple[tuple[str, float], ...] = (
    ("path_p10", 0.10),
    ("path_p25", 0.25),
    ("path_p50", 0.50),
    ("path_p75", 0.75),
    ("path_p90", 0.90),
)


def build_path_distribution(samples: pd.DataFrame) -> dict[str, float]:
    if "label_return_t1" not in samples.columns:
        raise ValueError("similarity samples missing label_return_t1")
    returns = pd.to_numeric(samples["label_return_t1"], errors="coerce").dropna().to_numpy(dtype=float)
    if len(returns) == 0:
        raise ValueError("similarity samples contain no valid returns")
    return {name: float(np.quantile(returns, quantile)) for name, quantile in PATH_QUANTILES}


def assert_ordered_distribution(distribution: dict[str, float]) -> None:
    values = [distribution[name] for name, _ in PATH_QUANTILES]
    if any(left > right for left, right in zip(values, values[1:])):
        raise ValueError("path distribution quantiles are not ordered")
