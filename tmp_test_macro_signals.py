from ai_research_studio.engines.macro_market.analyzers.impact_ranker import rank_macro_impacts
from ai_research_studio.engines.macro_market.analyzers.market_state_analyzer import analyze_market_state
from ai_research_studio.engines.macro_market.config import DEFAULT_MACRO_MARKET_CONFIG
from ai_research_studio.engines.macro_market.models import (
    MacroAssetSnapshot,
    MacroLLMSummary,
    MacroMarketContext,
    MacroMarketResult,
)
from ai_research_studio.engines.macro_market.renderer import render_macro_market_result
from ai_research_studio.engines.macro_market.signals import compute_macro_signals


def main() -> None:
    context = MacroMarketContext(
        generated_at="2026-03-03T00:00:00Z",
        crypto_assets={
            "BTC": MacroAssetSnapshot(
                symbol="BTC",
                name="Bitcoin",
                last_price=92000,
                change_24h_pct=1.8,
            ),
            "ETH": MacroAssetSnapshot(
                symbol="ETH",
                name="Ethereum",
                last_price=3200,
                change_24h_pct=2.4,
            ),
            "SOL": MacroAssetSnapshot(
                symbol="SOL",
                name="Solana",
                last_price=185,
                change_24h_pct=3.1,
            ),
        },
        macro_assets={
            "DXY": MacroAssetSnapshot(
                symbol="DXY",
                name="US Dollar Index",
                last_price=104.2,
                change_24h_pct=-0.4,
            ),
            "SPX": MacroAssetSnapshot(
                symbol="SPX",
                name="S&P 500",
                last_price=5950,
                change_24h_pct=1.2,
            ),
            "NDX": MacroAssetSnapshot(
                symbol="NDX",
                name="Nasdaq 100",
                last_price=21100,
                change_24h_pct=1.5,
            ),
            "US10Y": MacroAssetSnapshot(
                symbol="US10Y",
                name="US 10Y Treasury",
                last_price=4.23,
                change_24h_pct=-0.6,
            ),
        },
        news_items=[
            {"headline": "Fed officials signal a data-dependent stance", "importance": 0.9},
            {"headline": "Bitcoin ETF flows stabilize after recent volatility", "importance": 0.7},
        ],
        calendar_items=[
            {"title": "US Nonfarm Payrolls", "importance": 1.0},
            {"title": "Fed Chair speech", "importance": 0.8},
        ],
    )

    signals = compute_macro_signals(
        context,
        config=DEFAULT_MACRO_MARKET_CONFIG,
    )

    analysis = analyze_market_state(context, signals)
    analysis = rank_macro_impacts(context, signals, analysis)

    summary = MacroLLMSummary(
        headline="Risk-on backdrop with crypto confirmation.",
        summary="Cross-asset signals are supportive, with equities firm and long-end yields easing.",
        key_points=[
            "Crypto basket momentum is supportive.",
            "Equities remain constructive.",
            "Falling long-end yields are easing financial conditions.",
        ],
        risk_flags=[],
        watch_items=[
            "Monitor NFP for macro tone shift.",
            "Watch Fed Chair remarks for rates repricing.",
        ],
    )

    result = MacroMarketResult(
        context=context,
        signals=signals,
        analysis=analysis,
        summary=summary,
    )

    print("=== signals ===")
    print(signals)
    print()

    print("=== notes ===")
    for note in signals.notes:
        print("-", note)

    print()
    print("=== analysis ===")
    print(analysis)

    print()
    print("=== regime reasoning ===")
    for item in analysis.regime_reasoning:
        print("-", item)

    print()
    print("=== top drivers ===")
    for item in analysis.top_drivers:
        print("-", item)

    print()
    print("=== top risks ===")
    for item in analysis.top_risks:
        print("-", item)

    print()
    print("=== watch items ===")
    for item in analysis.watch_items:
        print("-", item)

    markdown_text = render_macro_market_result(result, target="markdown")
    telegram_text = render_macro_market_result(result, target="telegram")

    print()
    print("=== markdown ===")
    print(markdown_text)

    print()
    print("=== telegram ===")
    print(telegram_text)


if __name__ == "__main__":
    main()