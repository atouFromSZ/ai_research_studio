from __future__ import annotations

from ai_research_studio.engines.macro_market.config import MacroMarketConfig
from ai_research_studio.engines.macro_market.models import (
    MacroAssetSnapshot,
    MacroMarketContext,
    MacroSignalSet,
)


def _avg(values: list[float | None]) -> float | None:
    cleaned = [value for value in values if value is not None]
    if not cleaned:
        return None
    return sum(cleaned) / len(cleaned)


def _has_change(asset: MacroAssetSnapshot | None) -> bool:
    return asset is not None and asset.change_24h_pct is not None


def _get_change(asset: MacroAssetSnapshot | None) -> float | None:
    if asset is None:
        return None
    return asset.change_24h_pct


def _classify_crypto_momentum(
    *,
    crypto_avg_change: float | None,
    config: MacroMarketConfig,
    notes: list[str],
) -> str:
    if crypto_avg_change is None:
        notes.append("crypto momentum unavailable: no valid 24h change data")
        return "neutral"

    if crypto_avg_change >= config.bullish_change_threshold_pct:
        notes.append(f"crypto basket is strong: avg 24h change {crypto_avg_change:.2f}%")
        return "bullish"

    if crypto_avg_change <= config.bearish_change_threshold_pct:
        notes.append(f"crypto basket is weak: avg 24h change {crypto_avg_change:.2f}%")
        return "bearish"

    notes.append(f"crypto basket is mixed: avg 24h change {crypto_avg_change:.2f}%")
    return "neutral"


def _classify_equity_tone(
    *,
    equity_avg_change: float | None,
    config: MacroMarketConfig,
    notes: list[str],
) -> str:
    if equity_avg_change is None:
        notes.append("equity tone unavailable: no valid SPX/NDX change data")
        return "neutral"

    if equity_avg_change >= config.risk_on_equity_threshold_pct:
        notes.append(f"equities are supportive: avg 24h change {equity_avg_change:.2f}%")
        return "bullish"

    if equity_avg_change <= config.risk_off_equity_threshold_pct:
        notes.append(f"equities are weak: avg 24h change {equity_avg_change:.2f}%")
        return "bearish"

    notes.append(f"equities are mixed: avg 24h change {equity_avg_change:.2f}%")
    return "neutral"


def _classify_dollar_tone(
    *,
    dxy_change: float | None,
    config: MacroMarketConfig,
    notes: list[str],
) -> str:
    if dxy_change is None:
        notes.append("dollar tone unavailable: DXY 24h change missing")
        return "neutral"

    if dxy_change >= config.dollar_strong_threshold_pct:
        notes.append(f"dollar is strengthening: DXY 24h change {dxy_change:.2f}%")
        return "strong"

    if dxy_change <= config.dollar_weak_threshold_pct:
        notes.append(f"dollar is weakening: DXY 24h change {dxy_change:.2f}%")
        return "weak"

    notes.append(f"dollar is stable/mixed: DXY 24h change {dxy_change:.2f}%")
    return "neutral"


def _classify_rates_tone(
    *,
    us10y_change: float | None,
    config: MacroMarketConfig,
    notes: list[str],
) -> str:
    """
    v1 暂时使用 US10Y 的百分比变化近似利率环境变化。
    如果后面 collector 能提供 bp_change，再切换为 bp 逻辑更合理。
    """
    if us10y_change is None:
        notes.append("rates tone unavailable: US10Y 24h change missing")
        return "neutral"

    if us10y_change >= config.rates_rising_threshold_pct:
        notes.append(f"long-end yields are rising: US10Y 24h change {us10y_change:.2f}%")
        return "tightening"

    if us10y_change <= config.rates_falling_threshold_pct:
        notes.append(f"long-end yields are falling: US10Y 24h change {us10y_change:.2f}%")
        return "easing"

    notes.append(f"long-end yields are stable/mixed: US10Y 24h change {us10y_change:.2f}%")
    return "neutral"


def _classify_macro_risk_tone(
    *,
    equity_tone: str,
    dollar_tone: str,
    rates_tone: str,
    crypto_momentum: str,
    notes: list[str],
) -> str:
    """
    v1 规则尽量简单、可解释：
    - equities 强 + 美元不强 + 利率不紧 => risk_on
    - equities 弱 或 美元强 或 利率紧 => risk_off
    - 其余 => neutral

    crypto_momentum 在 v1 里主要作为辅助确认项，而不是主导项。
    """
    if (
        equity_tone == "bullish"
        and dollar_tone != "strong"
        and rates_tone != "tightening"
    ):
        if crypto_momentum == "bullish":
            notes.append("cross-asset tone aligns toward risk-on")
        else:
            notes.append("macro backdrop leans risk-on, though crypto confirmation is incomplete")
        return "risk_on"

    if (
        equity_tone == "bearish"
        or dollar_tone == "strong"
        or rates_tone == "tightening"
    ):
        if crypto_momentum == "bearish":
            notes.append("cross-asset tone aligns toward risk-off")
        else:
            notes.append("macro backdrop leans risk-off")
        return "risk_off"

    notes.append("cross-asset signals remain mixed")
    return "neutral"


def _compute_confidence(
    *,
    btc: MacroAssetSnapshot | None,
    eth: MacroAssetSnapshot | None,
    sol: MacroAssetSnapshot | None,
    spx: MacroAssetSnapshot | None,
    ndx: MacroAssetSnapshot | None,
    dxy: MacroAssetSnapshot | None,
    us10y: MacroAssetSnapshot | None,
) -> float:
    checks = [
        _has_change(btc),
        _has_change(eth),
        _has_change(sol),
        _has_change(spx),
        _has_change(ndx),
        _has_change(dxy),
        _has_change(us10y),
    ]
    available = sum(1 for item in checks if item)
    return available / len(checks)


def compute_macro_signals(
    context: MacroMarketContext,
    *,
    config: MacroMarketConfig,
) -> MacroSignalSet:
    notes: list[str] = []

    btc = context.crypto_assets.get("BTC")
    eth = context.crypto_assets.get("ETH")
    sol = context.crypto_assets.get("SOL")

    dxy = context.macro_assets.get("DXY")
    spx = context.macro_assets.get("SPX")
    ndx = context.macro_assets.get("NDX")
    us10y = context.macro_assets.get("US10Y")

    crypto_avg_change = _avg([
        _get_change(btc),
        _get_change(eth),
        _get_change(sol),
    ])

    equity_avg_change = _avg([
        _get_change(spx),
        _get_change(ndx),
    ])

    dxy_change = _get_change(dxy)
    us10y_change = _get_change(us10y)

    crypto_momentum = _classify_crypto_momentum(
        crypto_avg_change=crypto_avg_change,
        config=config,
        notes=notes,
    )
    equity_tone = _classify_equity_tone(
        equity_avg_change=equity_avg_change,
        config=config,
        notes=notes,
    )
    dollar_tone = _classify_dollar_tone(
        dxy_change=dxy_change,
        config=config,
        notes=notes,
    )
    rates_tone = _classify_rates_tone(
        us10y_change=us10y_change,
        config=config,
        notes=notes,
    )
    macro_risk_tone = _classify_macro_risk_tone(
        equity_tone=equity_tone,
        dollar_tone=dollar_tone,
        rates_tone=rates_tone,
        crypto_momentum=crypto_momentum,
        notes=notes,
    )

    confidence = _compute_confidence(
        btc=btc,
        eth=eth,
        sol=sol,
        spx=spx,
        ndx=ndx,
        dxy=dxy,
        us10y=us10y,
    )

    return MacroSignalSet(
        crypto_momentum=crypto_momentum,
        macro_risk_tone=macro_risk_tone,
        dollar_tone=dollar_tone,
        rates_tone=rates_tone,
        equity_tone=equity_tone,
        confidence=confidence,
        notes=notes,
    )