from __future__ import annotations

from ai_research_studio.engines.macro_market.formatters.markdown_formatter import (
    render_macro_market_markdown,
)
from ai_research_studio.engines.macro_market.formatters.telegram_formatter import (
    render_macro_market_telegram,
)
from ai_research_studio.engines.macro_market.models import MacroMarketResult


def render_macro_market_result(
    result: MacroMarketResult,
    *,
    target: str = "markdown",
) -> str:
    normalized_target = target.strip().lower()

    if normalized_target == "markdown":
        return render_macro_market_markdown(result)

    if normalized_target == "telegram":
        return render_macro_market_telegram(result)

    raise ValueError(f"Unsupported render target: {target}")