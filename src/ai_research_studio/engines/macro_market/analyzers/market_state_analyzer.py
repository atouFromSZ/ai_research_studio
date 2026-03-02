from __future__ import annotations

from ai_research_studio.engines.macro_market.models import (
    MacroMarketAnalysis,
    MacroMarketContext,
    MacroSignalSet,
)


def _pick_regime_label(signals: MacroSignalSet) -> str:
    """
    v1 先用最直接、最可解释的方式给市场贴标签。
    后面如果你想升级成 score model，再替换这里。
    """
    if signals.macro_risk_tone == "risk_on":
        if signals.crypto_momentum == "bullish":
            return "risk_on_with_crypto_confirmation"
        return "risk_on_but_crypto_mixed"

    if signals.macro_risk_tone == "risk_off":
        if signals.crypto_momentum == "bearish":
            return "risk_off_with_crypto_weakness"
        return "risk_off_but_crypto_resilient"

    if signals.crypto_momentum == "bullish":
        return "crypto_outperforming_in_mixed_macro"

    if signals.crypto_momentum == "bearish":
        return "crypto_weak_in_mixed_macro"

    return "mixed_neutral"


def _build_regime_reasoning(
    *,
    context: MacroMarketContext,
    signals: MacroSignalSet,
) -> list[str]:
    reasoning: list[str] = []

    # 先把 signals 里的 notes 吸收进来，作为最基础的解释层
    reasoning.extend(signals.notes[:5])

    # 再补一层更“归纳式”的解释
    if signals.macro_risk_tone == "risk_on":
        reasoning.append("macro backdrop currently favors risk-taking rather than defensive positioning.")
    elif signals.macro_risk_tone == "risk_off":
        reasoning.append("macro backdrop currently leans defensive and may pressure risk assets.")
    else:
        reasoning.append("macro backdrop remains mixed, without a clear cross-asset direction.")

    if signals.crypto_momentum == "bullish":
        reasoning.append("crypto price action is acting as a confirming or leading strength signal.")
    elif signals.crypto_momentum == "bearish":
        reasoning.append("crypto price action is acting as a confirming or leading weakness signal.")
    else:
        reasoning.append("crypto price action is not giving a strong directional confirmation.")

    # 如果有新闻/日历，给分析层留一句上下文提醒
    if context.news_items:
        reasoning.append("headline flow exists and may reinforce or disrupt the current regime.")
    if context.calendar_items:
        reasoning.append("upcoming macro events may shift the regime intraday.")

    return reasoning


def analyze_market_state(
    context: MacroMarketContext,
    signals: MacroSignalSet,
) -> MacroMarketAnalysis:
    regime_label = _pick_regime_label(signals)
    regime_reasoning = _build_regime_reasoning(
        context=context,
        signals=signals,
    )

    return MacroMarketAnalysis(
        regime_label=regime_label,
        regime_reasoning=regime_reasoning,
        top_drivers=[],
        top_risks=[],
        watch_items=[],
    )