# CNSVintraday V1.2 Feature Outputs

This directory is populated by the V1.2 Feature Engine pipeline.

Run:

```bash
python -m cnsvintraday.features.feature_store --data-root . --trade-date YYYYMMDD --snapshot-time 1400
```

Expected generated files:

- `data/features/feature_snapshot_1400.parquet`
- `data/features/feature_manifest.json`
- `data/features/feature_quality_latest.json`

The parquet snapshot is generated from T-day intraday snapshots at or before 14:00. It must not contain label, truth, future, t1, next, or actual fields.
