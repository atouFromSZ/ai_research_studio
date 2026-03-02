from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MacroMarketConfig:
    """macro_market 引擎配置。"""

    enable_llm_summary: bool = True
    enable_news_analysis: bool = True
    enable_calendar_analysis: bool = True

    persist_result: bool = False

    crypto_symbols: tuple[str, ...] = ("BTC", "ETH", "SOL")
    macro_symbols: tuple[str, ...] = ("DXY", "SPX", "NDX", "US10Y", "US2Y", "GOLD")

    bullish_change_threshold_pct: float = 2.0
    bearish_change_threshold_pct: float = -2.0

    risk_on_equity_threshold_pct: float = 1.0
    risk_off_equity_threshold_pct: float = -1.0

    dollar_strong_threshold_pct: float = 0.5
    dollar_weak_threshold_pct: float = -0.5

    # v1 暂时先用 change pct 近似，后面如果有 bp 数据再切换
    rates_rising_threshold_pct: float = 0.5
    rates_falling_threshold_pct: float = -0.5

    max_news_items: int = 8
    max_calendar_items: int = 8


DEFAULT_MACRO_MARKET_CONFIG = MacroMarketConfig()