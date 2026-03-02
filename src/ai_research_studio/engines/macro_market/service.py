from __future__ import annotations

from typing import Any

from ai_research_studio.engines.macro_market.config import (
    DEFAULT_MACRO_MARKET_CONFIG,
    MacroMarketConfig,
)
from ai_research_studio.engines.macro_market.models import MacroMarketResult
from ai_research_studio.engines.macro_market.workflows.generate_brief import (
    generate_macro_market_brief,
)


def run_macro_market_brief(
    *,
    config: MacroMarketConfig | None = None,
    crypto_market_items: list[dict[str, Any]] | None = None,
    macro_market_items: list[dict[str, Any]] | None = None,
    news_items: list[dict[str, Any]] | None = None,
    calendar_items: list[dict[str, Any]] | None = None,
    generated_at: str | None = None,
) -> MacroMarketResult:
    """
    macro_market 对外稳定入口。

    外部调用方（daily_brief / handlers / CLI / adapters）应优先调用这个函数，
    而不是直接依赖 workflow 内部实现。
    """
    effective_config = config or DEFAULT_MACRO_MARKET_CONFIG

    return generate_macro_market_brief(
        config=effective_config,
        crypto_market_items=crypto_market_items,
        macro_market_items=macro_market_items,
        news_items=news_items,
        calendar_items=calendar_items,
        generated_at=generated_at,
    )


def run_macro_market_markdown(
    *,
    config: MacroMarketConfig | None = None,
    crypto_market_items: list[dict[str, Any]] | None = None,
    macro_market_items: list[dict[str, Any]] | None = None,
    news_items: list[dict[str, Any]] | None = None,
    calendar_items: list[dict[str, Any]] | None = None,
    generated_at: str | None = None,
) -> str:
    result = run_macro_market_brief(
        config=config,
        crypto_market_items=crypto_market_items,
        macro_market_items=macro_market_items,
        news_items=news_items,
        calendar_items=calendar_items,
        generated_at=generated_at,
    )
    return result.markdown


def run_macro_market_telegram(
    *,
    config: MacroMarketConfig | None = None,
    crypto_market_items: list[dict[str, Any]] | None = None,
    macro_market_items: list[dict[str, Any]] | None = None,
    news_items: list[dict[str, Any]] | None = None,
    calendar_items: list[dict[str, Any]] | None = None,
    generated_at: str | None = None,
) -> str:
    result = run_macro_market_brief(
        config=config,
        crypto_market_items=crypto_market_items,
        macro_market_items=macro_market_items,
        news_items=news_items,
        calendar_items=calendar_items,
        generated_at=generated_at,
    )
    return result.telegram_text