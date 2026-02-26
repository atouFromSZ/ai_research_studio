from typing import Any

import requests

from ai_research_studio.settings import settings


def fetch_json(url: str, timeout: int = 10) -> dict[str, Any] | list[dict[str, Any]]:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fetch_binance_ticker(symbol: str) -> dict[str, Any]:
    url = f"{settings.binance_base_url}/api/v3/ticker/24hr"
    response = requests.get(url, params={"symbol": symbol}, timeout=settings.request_timeout)
    response.raise_for_status()
    return response.json()


def fetch_market_snapshot(symbols: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for symbol in symbols:
        data = fetch_binance_ticker(symbol)
        results.append(
            {
                "symbol": data["symbol"],
                "last_price": float(data["lastPrice"]),
                "price_change_percent": float(data["priceChangePercent"]),
                "high_price": float(data["highPrice"]),
                "low_price": float(data["lowPrice"]),
                "volume": float(data["volume"]),
                "quote_volume": float(data["quoteVolume"]),
            }
        )

    return results