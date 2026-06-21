from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cnsvintraday.features import FEATURE_VERSION


FEATURE_DEFINITIONS: list[dict[str, str]] = [
    {"feature_name": "return_1m", "description": "1 minute return", "source": "1min close", "formula": "close(t)/close(t-1)-1"},
    {"feature_name": "return_5m", "description": "5 minute return", "source": "1min close", "formula": "close(t)/close(t-5)-1"},
    {"feature_name": "return_15m", "description": "15 minute return", "source": "1min close", "formula": "close(t)/close(t-15)-1"},
    {"feature_name": "return_30m", "description": "30 minute return", "source": "1min close", "formula": "close(t)/close(t-30)-1"},
    {"feature_name": "return_60m", "description": "60 minute return", "source": "1min close", "formula": "close(t)/close(t-60)-1"},
    {"feature_name": "high_to_close", "description": "Close distance from intraday high", "source": "1min high/close", "formula": "close/high_until_t-1"},
    {"feature_name": "low_to_close", "description": "Close distance from intraday low", "source": "1min low/close", "formula": "close/low_until_t-1"},
    {"feature_name": "open_to_close", "description": "Open to current close return", "source": "1min open/close", "formula": "close/open_0930-1"},
    {"feature_name": "day_range_pct", "description": "Intraday range normalized by open", "source": "1min high/low/open", "formula": "(high-low)/open"},
    {"feature_name": "close_position", "description": "Close position inside intraday range", "source": "1min high/low/close", "formula": "(close-low)/(high-low)"},
    {"feature_name": "volume_1m", "description": "Latest minute volume", "source": "1min volume", "formula": "volume(t)"},
    {"feature_name": "volume_5m", "description": "Trailing 5 minute volume", "source": "1min volume", "formula": "sum(volume, 5)"},
    {"feature_name": "volume_15m", "description": "Trailing 15 minute volume", "source": "1min volume", "formula": "sum(volume, 15)"},
    {"feature_name": "volume_ratio_5m", "description": "5 minute volume vs average pace", "source": "1min volume", "formula": "sum(volume, 5)/(avg_1m_volume*5)"},
    {"feature_name": "volume_ratio_15m", "description": "15 minute volume vs average pace", "source": "1min volume", "formula": "sum(volume, 15)/(avg_1m_volume*15)"},
    {"feature_name": "volume_ratio_30m", "description": "30 minute volume vs average pace", "source": "1min volume", "formula": "sum(volume, 30)/(avg_1m_volume*30)"},
    {"feature_name": "volume_acceleration", "description": "Latest 5 minute volume acceleration", "source": "1min volume", "formula": "(last_5m-prev_5m)/prev_5m"},
    {"feature_name": "turnover_ratio", "description": "Amount over close adjusted volume", "source": "1min amount/volume/close", "formula": "sum(amount)/(close*sum(volume))"},
    {"feature_name": "vwap", "description": "Cumulative VWAP", "source": "1min amount/volume", "formula": "sum(amount)/sum(volume)"},
    {"feature_name": "distance_to_vwap", "description": "Close distance from VWAP", "source": "1min close/amount/volume", "formula": "close/vwap-1"},
    {"feature_name": "price_above_vwap", "description": "Close above VWAP flag", "source": "1min close/vwap", "formula": "1 if close>=vwap else 0"},
    {"feature_name": "vwap_trend", "description": "Second half VWAP over first half VWAP", "source": "1min amount/volume", "formula": "vwap_second/vwap_first-1"},
    {"feature_name": "ma5", "description": "5 minute moving average", "source": "1min close", "formula": "mean(close, 5)"},
    {"feature_name": "ma10", "description": "10 minute moving average", "source": "1min close", "formula": "mean(close, 10)"},
    {"feature_name": "ma20", "description": "20 minute moving average", "source": "1min close", "formula": "mean(close, 20)"},
    {"feature_name": "price_above_ma5", "description": "Close above MA5 flag", "source": "1min close", "formula": "1 if close>=ma5 else 0"},
    {"feature_name": "price_above_ma10", "description": "Close above MA10 flag", "source": "1min close", "formula": "1 if close>=ma10 else 0"},
    {"feature_name": "price_above_ma20", "description": "Close above MA20 flag", "source": "1min close", "formula": "1 if close>=ma20 else 0"},
    {"feature_name": "ma5_slope", "description": "MA5 trailing slope", "source": "1min close", "formula": "ma5(t)/ma5(t-5)-1"},
    {"feature_name": "ma10_slope", "description": "MA10 trailing slope", "source": "1min close", "formula": "ma10(t)/ma10(t-10)-1"},
    {"feature_name": "ma20_slope", "description": "MA20 trailing slope", "source": "1min close", "formula": "ma20(t)/ma20(t-20)-1"},
    {"feature_name": "high_break", "description": "Close breaks prior intraday high", "source": "1min high/close", "formula": "1 if close > max(high[:-1]) else 0"},
    {"feature_name": "low_break", "description": "Close breaks prior intraday low", "source": "1min low/close", "formula": "1 if close < min(low[:-1]) else 0"},
    {"feature_name": "new_high_intraday", "description": "Latest bar made intraday high", "source": "1min high", "formula": "1 if high(t)>=max(high) else 0"},
    {"feature_name": "new_low_intraday", "description": "Latest bar made intraday low", "source": "1min low", "formula": "1 if low(t)<=min(low) else 0"},
    {"feature_name": "close_strength", "description": "Close strength inside intraday range", "source": "1min high/low/close", "formula": "(close-low)/(high-low)"},
    {"feature_name": "intraday_strength_score", "description": "Composite intraday strength score", "source": "price features", "formula": "average(close_strength, bounded_open_to_close)"},
]


def feature_names() -> list[str]:
    return [item["feature_name"] for item in FEATURE_DEFINITIONS]


def build_feature_manifest() -> dict[str, Any]:
    return {
        "feature_version": FEATURE_VERSION,
        "feature_count": len(FEATURE_DEFINITIONS),
        "features": [{**item, "created_version": FEATURE_VERSION} for item in FEATURE_DEFINITIONS],
    }


def write_feature_manifest(path: Path) -> dict[str, Any]:
    manifest = build_feature_manifest()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest
