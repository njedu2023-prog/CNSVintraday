from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from cnsvintraday.models.labels import build_t1_labels
from cnsvintraday.models.replay_engine import build_baseline_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run CNSVintraday V1.3 baseline model pipeline")
    parser.add_argument("--data-root", default=".")
    parser.add_argument("--feature-path", default="data/features/feature_snapshot_1400.parquet")
    parser.add_argument("--label-source-path", required=True)
    parser.add_argument("--snapshot-time", default="1400")
    parser.add_argument("--train-window", type=int, default=150)
    args = parser.parse_args(argv)

    data_root = Path(args.data_root)
    features = pd.read_parquet(data_root / args.feature_path)
    label_source = pd.read_parquet(data_root / args.label_source_path)
    labels = build_t1_labels(label_source)
    summary = build_baseline_outputs(
        data_root,
        features,
        labels,
        snapshot_time=args.snapshot_time,
        train_window=args.train_window,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
