from typing import Any

import requests

from ai_research_studio.settings import settings


def fetch_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    response = requests.get(url, params=params, timeout=settings.request_timeout)
    response.raise_for_status()
    return response.json()


def fetch_binance_ticker(symbol: str) -> dict[str, Any]:
    url = f"{settings.binance_base_url}/api/v3/ticker/24hr"
    return fetch_json(url, params={"symbol": symbol})


def fetch_market_snapshot(symbols: list[str]) -> list[dict[str, Any]]:
    snapshot: list[dict[str, Any]] = []

    for symbol in symbols:
        data = fetch_binance_ticker(symbol)

        snapshot.append(
            {
                "symbol": symbol,
                "last_price": float(data["lastPrice"]),
                "price_change_percent": float(data["priceChangePercent"]),
                "high_price": float(data["highPrice"]),
                "low_price": float(data["lowPrice"]),
                "volume": float(data["volume"]),
                "quote_volume": float(data["quoteVolume"]),
            }
        )

    return snapshot
