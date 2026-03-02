from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ai_research_studio.engines.macro_market.analyzers.impact_ranker import (
    rank_macro_impacts,
)
from ai_research_studio.engines.macro_market.analyzers.market_state_analyzer import (
    analyze_market_state,
)
from ai_research_studio.engines.macro_market.config import (
    DEFAULT_MACRO_MARKET_CONFIG,
    MacroMarketConfig,
)
from ai_research_studio.engines.macro_market.models import (
    MacroAssetSnapshot,
    MacroLLMSummary,
    MacroMarketContext,
    MacroMarketResult,
)
from ai_research_studio.engines.macro_market.renderer import render_macro_market_result
from ai_research_studio.engines.macro_market.signals import compute_macro_signals


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _normalize_asset_item(item: dict[str, Any]) -> MacroAssetSnapshot | None:
    raw_symbol = str(item.get("symbol", "")).strip().upper()
    if not raw_symbol:
        return None

    normalized_symbol = raw_symbol

    # 兼容 Binance 常见交易对写法，映射到 macro_market 内部期望的基础资产符号
    quote_suffixes = ("USDT", "USDC", "FDUSD", "BUSD", "USD")
    for suffix in quote_suffixes:
        if raw_symbol.endswith(suffix) and len(raw_symbol) > len(suffix):
            normalized_symbol = raw_symbol[: -len(suffix)]
            break

    name = str(item.get("name", normalized_symbol)).strip() or normalized_symbol

    return MacroAssetSnapshot(
        symbol=normalized_symbol,
        name=name,
        last_price=_safe_float(item.get("last_price")),
        change_24h_pct=_safe_float(item.get("price_change_percent")),
        high_24h=_safe_float(item.get("high_price")),
        low_24h=_safe_float(item.get("low_price")),
        volume_24h=_safe_float(item.get("volume")),
        extra={
            "raw_symbol": raw_symbol,
            **{
                key: value
                for key, value in item.items()
                if key
                not in {
                    "symbol",
                    "name",
                    "last_price",
                    "price_change_percent",
                    "high_price",
                    "low_price",
                    "volume",
                }
            },
        },
    )


def _build_asset_map(items: list[dict[str, Any]] | None) -> dict[str, MacroAssetSnapshot]:
    asset_map: dict[str, MacroAssetSnapshot] = {}

    for item in items or []:
        asset = _normalize_asset_item(item)
        if asset is None:
            continue
        asset_map[asset.symbol] = asset

    return asset_map


def build_macro_market_context(
    *,
    crypto_market_items: list[dict[str, Any]] | None = None,
    macro_market_items: list[dict[str, Any]] | None = None,
    news_items: list[dict[str, Any]] | None = None,
    calendar_items: list[dict[str, Any]] | None = None,
    generated_at: str | None = None,
) -> MacroMarketContext:
    return MacroMarketContext(
        generated_at=generated_at or datetime.now(UTC).isoformat(),
        crypto_assets=_build_asset_map(crypto_market_items),
        macro_assets=_build_asset_map(macro_market_items),
        news_items=list(news_items or []),
        calendar_items=list(calendar_items or []),
        raw_payloads={
            "crypto_market_items": list(crypto_market_items or []),
            "macro_market_items": list(macro_market_items or []),
            "news_items": list(news_items or []),
            "calendar_items": list(calendar_items or []),
        },
    )


def build_fallback_summary(
    context: MacroMarketContext,
    result: MacroMarketResult,
) -> MacroLLMSummary:
    signals = result.signals
    analysis = result.analysis

    headline = (
        f"{analysis.regime_label} | "
        f"risk={signals.macro_risk_tone} | "
        f"crypto={signals.crypto_momentum}"
    )

    summary_parts: list[str] = []
    if analysis.top_drivers:
        summary_parts.append(f"Drivers: {'; '.join(analysis.top_drivers[:2])}")
    if analysis.top_risks:
        summary_parts.append(f"Risks: {'; '.join(analysis.top_risks[:2])}")
    if not summary_parts:
        summary_parts.append("No dominant driver or risk cluster was detected from the current inputs.")

    return MacroLLMSummary(
        headline=headline,
        summary=" ".join(summary_parts),
        key_points=list(analysis.top_drivers[:3]),
        risk_flags=list(analysis.top_risks[:3]),
        watch_items=list(analysis.watch_items[:3]),
        raw_text="",
    )


def generate_macro_market_brief(
    *,
    config: MacroMarketConfig | None = None,
    crypto_market_items: list[dict[str, Any]] | None = None,
    macro_market_items: list[dict[str, Any]] | None = None,
    news_items: list[dict[str, Any]] | None = None,
    calendar_items: list[dict[str, Any]] | None = None,
    generated_at: str | None = None,
) -> MacroMarketResult:
    effective_config = config or DEFAULT_MACRO_MARKET_CONFIG

    context = build_macro_market_context(
        crypto_market_items=crypto_market_items,
        macro_market_items=macro_market_items,
        news_items=news_items,
        calendar_items=calendar_items,
        generated_at=generated_at,
    )

    signals = compute_macro_signals(
        context,
        config=effective_config,
    )

    analysis = analyze_market_state(context, signals)
    analysis = rank_macro_impacts(context, signals, analysis)

    result = MacroMarketResult(
        context=context,
        signals=signals,
        analysis=analysis,
    )

    # v1 先用 deterministic fallback summary。
    # 下一步再在这里接 shared/llm。
    result.summary = build_fallback_summary(context, result)

    result.markdown = render_macro_market_result(result, target="markdown")
    result.telegram_text = render_macro_market_result(result, target="telegram")

    return result