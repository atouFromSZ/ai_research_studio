from __future__ import annotations

from typing import Any

import requests

from ai_research_studio.settings import settings


def fetch_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    response = requests.get(url, params=params, timeout=settings.request_timeout)
    response.raise_for_status()
    return response.json()


def fetch_binance_ticker_raw(symbol: str) -> dict[str, Any]:
    url = "https://api.binance.com/api/v3/ticker/24hr"
    return fetch_json(url, params={"symbol": symbol})


def normalize_binance_ticker(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol": data.get("symbol", "UNKNOWN"),
        "last_price": float(data.get("lastPrice", 0)),
        "price_change_percent": float(data.get("priceChangePercent", 0)),
        "high_price": float(data.get("highPrice", 0)),
        "low_price": float(data.get("lowPrice", 0)),
        "volume": float(data.get("volume", 0)),
        "quote_volume": float(data.get("quoteVolume", 0)),
    }


def fetch_binance_ticker(symbol: str) -> dict[str, Any]:
    raw = fetch_binance_ticker_raw(symbol)
    return normalize_binance_ticker(raw)


def fetch_market_snapshot(symbols: list[str]) -> list[dict[str, Any]]:
    return [fetch_binance_ticker(symbol) for symbol in symbols]