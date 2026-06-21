# CNSVintraday V1.2 Feature Dashboard

This directory is populated by the V1.2 Feature Engine pipeline.

Run:

```bash
python -m cnsvintraday.features.feature_store --data-root . --trade-date YYYYMMDD --snapshot-time 1400
```

Expected generated file:

- `docs/features/feature_dashboard.html`

The dashboard summarizes the feature contract, feature count, quality status, missing rate, abnormal count, and latest generated time.
