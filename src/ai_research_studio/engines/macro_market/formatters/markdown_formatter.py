from __future__ import annotations

from ai_research_studio.engines.macro_market.models import (
    MacroAssetSnapshot,
    MacroMarketResult,
)


def _format_price(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.4f}"


def _format_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"


def _render_asset_line(asset: MacroAssetSnapshot) -> str:
    return (
        f"- **{asset.symbol}**: "
        f"{_format_price(asset.last_price)} "
        f"({_format_pct(asset.change_24h_pct)})"
    )


def _render_section_list(title: str, items: list[str]) -> list[str]:
    lines: list[str] = [f"## {title}"]
    if not items:
        lines.append("- None")
        lines.append("")
        return lines

    for item in items:
        lines.append(f"- {item}")
    lines.append("")
    return lines


def render_macro_market_markdown(result: MacroMarketResult) -> str:
    context = result.context
    signals = result.signals
    analysis = result.analysis
    summary = result.summary

    lines: list[str] = []
    lines.append("# Macro Market")
    lines.append("")
    lines.append(f"**Generated At:** {context.generated_at}")
    lines.append("")

    lines.append("## Regime Snapshot")
    lines.append(f"- **Regime Label:** {analysis.regime_label}")
    lines.append(f"- **Macro Risk Tone:** {signals.macro_risk_tone}")
    lines.append(f"- **Crypto Momentum:** {signals.crypto_momentum}")
    lines.append(f"- **Dollar Tone:** {signals.dollar_tone}")
    lines.append(f"- **Rates Tone:** {signals.rates_tone}")
    lines.append(f"- **Equity Tone:** {signals.equity_tone}")
    lines.append(f"- **Confidence:** {signals.confidence:.2f}")
    lines.append("")

    # 收口版：去掉 Crypto Snapshot，避免和日报里的 Major Assets / Watchlist 重复
    if context.macro_assets:
        lines.append("## Macro Snapshot")
        for symbol in ("DXY", "SPX", "NDX", "US10Y", "US2Y", "GOLD"):
            asset = context.macro_assets.get(symbol)
            if asset:
                lines.append(_render_asset_line(asset))
        lines.append("")

    if summary.headline:
        lines.append("## Headline")
        lines.append(summary.headline)
        lines.append("")

    if summary.summary:
        lines.append("## Summary")
        lines.append(summary.summary)
        lines.append("")

    lines.extend(_render_section_list("Regime Reasoning", analysis.regime_reasoning))
    lines.extend(_render_section_list("Top Drivers", analysis.top_drivers))
    lines.extend(_render_section_list("Top Risks", analysis.top_risks))
    lines.extend(_render_section_list("Watch Items", analysis.watch_items))

    if summary.key_points:
        lines.extend(_render_section_list("Key Points", summary.key_points))
    if summary.risk_flags:
        lines.extend(_render_section_list("Risk Flags", summary.risk_flags))
    if summary.watch_items:
        lines.extend(_render_section_list("LLM Watch Items", summary.watch_items))

    return "\n".join(lines).strip()