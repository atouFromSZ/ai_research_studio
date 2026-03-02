from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MacroAssetSnapshot:
    """单个资产/指标的标准化快照。"""

    symbol: str
    name: str
    last_price: float | None = None
    change_24h_pct: float | None = None
    high_24h: float | None = None
    low_24h: float | None = None
    volume_24h: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MacroSignalSet:
    """deterministic 规则层输出。"""

    crypto_momentum: str = "neutral"
    macro_risk_tone: str = "neutral"
    dollar_tone: str = "neutral"
    rates_tone: str = "neutral"
    equity_tone: str = "neutral"
    confidence: float = 0.0
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MacroLLMSummary:
    """LLM 或 fallback summarizer 的结构化输出。"""

    headline: str = ""
    summary: str = ""
    key_points: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    watch_items: list[str] = field(default_factory=list)
    raw_text: str = ""


@dataclass(slots=True)
class MacroMarketContext:
    """
    macro_market 工作流中的统一上下文对象。
    collectors 的输出、归一化后的资产数据、新闻、事件日历等都收敛到这里。
    """

    generated_at: str
    crypto_assets: dict[str, MacroAssetSnapshot] = field(default_factory=dict)
    macro_assets: dict[str, MacroAssetSnapshot] = field(default_factory=dict)
    news_items: list[dict[str, Any]] = field(default_factory=list)
    calendar_items: list[dict[str, Any]] = field(default_factory=list)
    raw_payloads: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MacroMarketAnalysis:
    """高层分析层输出，供 formatter / summarizer 使用。"""

    regime_label: str = "neutral"
    regime_reasoning: list[str] = field(default_factory=list)
    top_drivers: list[str] = field(default_factory=list)
    top_risks: list[str] = field(default_factory=list)
    watch_items: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MacroMarketResult:
    """macro_market 引擎最终输出对象。"""

    context: MacroMarketContext
    signals: MacroSignalSet
    analysis: MacroMarketAnalysis = field(default_factory=MacroMarketAnalysis)
    summary: MacroLLMSummary = field(default_factory=MacroLLMSummary)
    markdown: str = ""
    telegram_text: str = ""
    storage_path: str | None = None