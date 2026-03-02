from __future__ import annotations

from typing import Any

from ai_research_studio.engines.macro_market.models import (
    MacroMarketAnalysis,
    MacroMarketContext,
    MacroSignalSet,
)


def _pick_text(item: dict[str, Any]) -> str:
    """
    尝试从不同结构的 news/calendar item 里抽取最适合展示的一段文字。
    v1 不做复杂 schema 兼容，只做宽松兜底。
    """
    for key in ("headline", "title", "summary", "text", "name"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Untitled item"


def _pick_importance(item: dict[str, Any]) -> float:
    """
    v1 允许外部 collector 传 importance / score；
    没有的话默认按 0.0 处理。
    """
    value = item.get("importance", item.get("score", 0.0))
    try:
        return float(value)
    except Exception:
        return 0.0


def _sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=_pick_importance, reverse=True)


def _derive_driver_from_signals(signals: MacroSignalSet) -> list[str]:
    drivers: list[str] = []

    if signals.macro_risk_tone == "risk_on":
        drivers.append("Cross-asset backdrop is leaning risk-on.")
    elif signals.macro_risk_tone == "risk_off":
        drivers.append("Cross-asset backdrop is leaning risk-off.")

    if signals.crypto_momentum == "bullish":
        drivers.append("Crypto basket momentum is supportive.")
    elif signals.crypto_momentum == "bearish":
        drivers.append("Crypto basket momentum is weak.")

    if signals.equity_tone == "bullish":
        drivers.append("Equities are contributing a supportive signal.")
    elif signals.equity_tone == "bearish":
        drivers.append("Equities are contributing a negative signal.")

    if signals.dollar_tone == "weak":
        drivers.append("A softer dollar is supportive for risk assets.")
    elif signals.dollar_tone == "strong":
        drivers.append("A stronger dollar is a headwind for risk assets.")

    if signals.rates_tone == "easing":
        drivers.append("Falling long-end yields are easing financial conditions.")
    elif signals.rates_tone == "tightening":
        drivers.append("Rising long-end yields are tightening financial conditions.")

    return drivers[:5]


def _derive_risks_from_signals(signals: MacroSignalSet) -> list[str]:
    risks: list[str] = []

    if signals.dollar_tone == "strong":
        risks.append("Dollar strength may pressure crypto and broader risk assets.")

    if signals.rates_tone == "tightening":
        risks.append("Rising long-end yields may tighten liquidity conditions.")

    if signals.equity_tone == "bearish":
        risks.append("Weak equities may drag down broader risk sentiment.")

    if signals.crypto_momentum == "bearish":
        risks.append("Crypto short-term momentum remains fragile.")

    if signals.confidence < 0.6:
        risks.append("Signal confidence is limited because data coverage is incomplete.")

    return risks[:5]


def _derive_watch_items_from_calendar(
    calendar_items: list[dict[str, Any]],
    *,
    limit: int = 5,
) -> list[str]:
    if not calendar_items:
        return []

    ranked = _sort_items(calendar_items)
    watch_items: list[str] = []

    for item in ranked[:limit]:
        text = _pick_text(item)
        watch_items.append(f"Upcoming event: {text}")

    return watch_items


def _derive_watch_items_from_news(
    news_items: list[dict[str, Any]],
    *,
    limit: int = 5,
) -> list[str]:
    if not news_items:
        return []

    ranked = _sort_items(news_items)
    watch_items: list[str] = []

    for item in ranked[:limit]:
        text = _pick_text(item)
        watch_items.append(f"Headline flow to monitor: {text}")

    return watch_items


def rank_macro_impacts(
    context: MacroMarketContext,
    signals: MacroSignalSet,
    analysis: MacroMarketAnalysis,
) -> MacroMarketAnalysis:
    top_drivers = list(analysis.top_drivers)
    top_risks = list(analysis.top_risks)
    watch_items = list(analysis.watch_items)

    top_drivers.extend(_derive_driver_from_signals(signals))
    top_risks.extend(_derive_risks_from_signals(signals))
    watch_items.extend(_derive_watch_items_from_calendar(context.calendar_items))
    watch_items.extend(_derive_watch_items_from_news(context.news_items))

    # 去重，同时保留顺序
    def _dedupe_keep_order(items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            normalized = item.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)
        return result

    return MacroMarketAnalysis(
        regime_label=analysis.regime_label,
        regime_reasoning=list(analysis.regime_reasoning),
        top_drivers=_dedupe_keep_order(top_drivers)[:5],
        top_risks=_dedupe_keep_order(top_risks)[:5],
        watch_items=_dedupe_keep_order(watch_items)[:8],
    )
    