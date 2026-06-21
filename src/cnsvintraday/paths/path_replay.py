from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from cnsvintraday.models.labels import build_t1_labels
from cnsvintraday.paths import PATH_DISTRIBUTION_VERSION
from cnsvintraday.paths.path_dashboard import write_path_dashboard
from cnsvintraday.paths.path_distribution import assert_ordered_distribution, build_path_distribution
from cnsvintraday.paths.path_metrics import write_path_metrics
from cnsvintraday.paths.price_band import build_price_band
from cnsvintraday.paths.risk_engine import build_risk_summary
from cnsvintraday.paths.similarity_engine import SimilarityConfig, find_similar_samples, path_feature_columns


def path_output_paths(data_root: Path) -> dict[str, Path]:
    return {
        "distribution": data_root / "data" / "paths" / "path_distribution_latest.parquet",
        "metrics": data_root / "data" / "paths" / "path_metrics_latest.json",
        "similarity": data_root / "data" / "paths" / "similarity_samples_latest.parquet",
        "dashboard": data_root / "docs" / "paths" / "path_dashboard.html",
    }


def prepare_path_frame(features: pd.DataFrame, label_source: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    labels = build_t1_labels(label_source)
    prices = label_source[["trade_date", "price_1400"]].copy()
    merged = (
        features.merge(labels, on="trade_date", how="inner")
        .merge(prices, on="trade_date", how="left")
        .sort_values("trade_date")
        .reset_index(drop=True)
    )
    if merged.empty:
        raise ValueError("path frame is empty after joining features and labels")
    if merged["price_1400"].isna().any():
        raise ValueError("path frame missing price_1400")
    return merged, path_feature_columns(features)


def run_path_replay(
    features: pd.DataFrame,
    label_source: pd.DataFrame,
    config: SimilarityConfig | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    config = config or SimilarityConfig()
    frame, columns = prepare_path_frame(features, label_source)
    if len(frame) <= config.lookback_days:
        raise ValueError(f"history insufficient for path replay: need more than {config.lookback_days}, got {len(frame)}")

    path_records: list[dict[str, object]] = []
    sample_records: list[dict[str, object]] = []
    for index in range(config.lookback_days, len(frame)):
        history = frame.iloc[index - config.lookback_days : index]
        current = frame.iloc[index]
        samples = find_similar_samples(history, current, columns, sample_count=config.sample_count)
        distribution = build_path_distribution(samples)
        assert_ordered_distribution(distribution)
        price_band = build_price_band(float(current["price_1400"]), distribution)
        risk = build_risk_summary(distribution)
        path_records.append(
            {
                "trade_date": str(current["trade_date"]),
                "next_trade_date": str(current["next_trade_date"]),
                "path_version": PATH_DISTRIBUTION_VERSION,
                **distribution,
                **price_band,
                **risk,
                "label_return_t1": float(current["label_return_t1"]),
            }
        )
        for sample in samples.to_dict("records"):
            sample_records.append(
                {
                    "target_trade_date": str(current["trade_date"]),
                    "sample_trade_date": str(sample["trade_date"]),
                    "similarity_rank": int(sample["similarity_rank"]),
                    "distance": float(sample["distance"]),
                    "sample_return_t1": float(sample["label_return_t1"]),
                }
            )
    return pd.DataFrame(path_records), pd.DataFrame(sample_records)


def build_path_outputs(
    data_root: Path,
    features: pd.DataFrame,
    label_source: pd.DataFrame,
    lookback_days: int = 150,
    sample_count: int = 20,
) -> dict[str, Any]:
    config = SimilarityConfig(lookback_days=lookback_days, sample_count=sample_count)
    replay, samples = run_path_replay(features, label_source, config)
    paths = path_output_paths(data_root)
    for output_path in paths.values():
        output_path.parent.mkdir(parents=True, exist_ok=True)
    distribution = replay.drop(columns=["label_return_t1"])
    distribution.to_parquet(paths["distribution"], index=False)
    samples.to_parquet(paths["similarity"], index=False)
    metrics = write_path_metrics(replay, paths["metrics"])
    write_path_dashboard(distribution, metrics, paths["dashboard"])
    return {
        "path_distribution_version": PATH_DISTRIBUTION_VERSION,
        "prediction_count": int(len(distribution)),
        "sample_count": int(len(samples)),
        "metrics": metrics,
        "paths": {key: str(path) for key, path in paths.items()},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build CNSVintraday V1.4 path distribution outputs.")
    parser.add_argument("--data-root", default=".", help="Repository or data root.")
    parser.add_argument("--feature-path", default="data/features/feature_snapshot_1400.parquet")
    parser.add_argument("--label-source-path", required=True)
    parser.add_argument("--lookback-days", type=int, default=150)
    parser.add_argument("--sample-count", type=int, default=20)
    args = parser.parse_args(argv)

    data_root = Path(args.data_root)
    features = pd.read_parquet(data_root / args.feature_path)
    label_source = pd.read_parquet(data_root / args.label_source_path)
    build_path_outputs(data_root, features, label_source, lookback_days=args.lookback_days, sample_count=args.sample_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

