from __future__ import annotations


PATH_TO_PRICE_COLUMNS = {
    "path_p10": "price_p10",
    "path_p25": "price_p25",
    "path_p50": "price_p50",
    "path_p75": "price_p75",
    "path_p90": "price_p90",
}


def build_price_band(price_1400: float, distribution: dict[str, float]) -> dict[str, float]:
    price = float(price_1400)
    if price <= 0:
        raise ValueError("price_1400 must be positive")
    return {price_name: price * (1.0 + float(distribution[path_name])) for path_name, price_name in PATH_TO_PRICE_COLUMNS.items()}

