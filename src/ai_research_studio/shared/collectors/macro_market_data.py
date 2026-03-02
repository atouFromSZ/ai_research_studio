from __future__ import annotations

from typing import Any

import requests

from ai_research_studio.settings import settings


FRED_SERIES_MAP: dict[str, dict[str, str]] = {
    "SPX": {
        "series_id": "SP500",
        "name": "S&P 500",
    },
    "NDX": {
        "series_id": "NASDAQ100",
        "name": "NASDAQ-100",
    },
    "US10Y": {
        "series_id": "DGS10",
        "name": "US 10Y Treasury Yield",
    },
    "US2Y": {
        "series_id": "DGS2",
        "name": "US 2Y Treasury Yield",
    },
    # v1 先用 FRED 的广义美元指数代理美元强弱，不等同于经典 DXY
    "DXY": {
        "series_id": "DTWEXBGS",
        "name": "Nominal Broad U.S. Dollar Index",
    },
}


def _get_fred_api_key() -> str:
    api_key = getattr(settings, "fred_api_key", "") or ""
    return str(api_key).strip()


def _fetch_fred_observations(series_id: str, limit: int = 5) -> list[dict[str, Any]]:
    api_key = _get_fred_api_key()
    if not api_key:
        raise RuntimeError(
            "FRED API key is missing. Please set settings.fred_api_key before fetching macro market data."
        )

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }

    response = requests.get(url, params=params, timeout=settings.request_timeout)
    response.raise_for_status()

    payload = response.json()
    observations = payload.get("observations", [])
    if not isinstance(observations, list):
        return []
    return observations


def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, "", "."):
            return None
        return float(value)
    except Exception:
        return None


def _pick_latest_two_valid_values(observations: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    valid_values: list[float] = []

    for item in observations:
        value = _safe_float(item.get("value"))
        if value is None:
            continue
        valid_values.append(value)
        if len(valid_values) >= 2:
            break

    latest = valid_values[0] if len(valid_values) >= 1 else None
    previous = valid_values[1] if len(valid_values) >= 2 else None
    return latest, previous


def _calc_change_pct(latest: float | None, previous: float | None) -> float | None:
    if latest is None or previous is None:
        return None
    if previous == 0:
        return None
    return ((latest - previous) / previous) * 100.0


def fetch_fred_macro_item(symbol: str) -> dict[str, Any]:
    symbol = symbol.strip().upper()
    if symbol not in FRED_SERIES_MAP:
        raise ValueError(f"Unsupported macro symbol: {symbol}")

    meta = FRED_SERIES_MAP[symbol]
    observations = _fetch_fred_observations(meta["series_id"], limit=5)
    latest, previous = _pick_latest_two_valid_values(observations)
    change_pct = _calc_change_pct(latest, previous)

    return {
        "symbol": symbol,
        "name": meta["name"],
        "last_price": latest,
        "price_change_percent": change_pct,
        "high_price": None,
        "low_price": None,
        "volume": None,
        "source": "fred",
        "series_id": meta["series_id"],
        "previous_value": previous,
    }


def fetch_macro_market_snapshot(symbols: list[str]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    for symbol in symbols:
        try:
            items.append(fetch_fred_macro_item(symbol))
        except Exception:
            # v1 先容错跳过单个失败项，避免一个序列失败拖垮整组宏观数据
            continue

    return items