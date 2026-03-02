from ai_research_studio.engines.macro_market.workflows.generate_brief import (
    generate_macro_market_brief,
)


def main() -> None:
    result = generate_macro_market_brief(
        generated_at="2026-03-03T00:00:00Z",
        crypto_market_items=[
            {"symbol": "BTC", "name": "Bitcoin", "last_price": 92000, "price_change_percent": 1.8},
            {"symbol": "ETH", "name": "Ethereum", "last_price": 3200, "price_change_percent": 2.4},
            {"symbol": "SOL", "name": "Solana", "last_price": 185, "price_change_percent": 3.1},
        ],
        macro_market_items=[
            {"symbol": "DXY", "name": "US Dollar Index", "last_price": 104.2, "price_change_percent": -0.4},
            {"symbol": "SPX", "name": "S&P 500", "last_price": 5950, "price_change_percent": 1.2},
            {"symbol": "NDX", "name": "Nasdaq 100", "last_price": 21100, "price_change_percent": 1.5},
            {"symbol": "US10Y", "name": "US 10Y Treasury", "last_price": 4.23, "price_change_percent": -0.6},
        ],
        news_items=[
            {"headline": "Fed officials signal a data-dependent stance", "importance": 0.9},
            {"headline": "Bitcoin ETF flows stabilize after recent volatility", "importance": 0.7},
        ],
        calendar_items=[
            {"title": "US Nonfarm Payrolls", "importance": 1.0},
            {"title": "Fed Chair speech", "importance": 0.8},
        ],
    )

    print("=== regime_label ===")
    print(result.analysis.regime_label)
    print()

    print("=== summary ===")
    print(result.summary)
    print()

    print("=== markdown ===")
    print(result.markdown)
    print()

    print("=== telegram ===")
    print(result.telegram_text)


if __name__ == "__main__":
    main()