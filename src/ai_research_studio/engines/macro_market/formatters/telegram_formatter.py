from __future__ import annotations

from ai_research_studio.engines.macro_market.models import MacroMarketResult


def _render_lines(title: str, items: list[str], *, limit: int = 3) -> list[str]:
    lines: list[str] = [title]
    if not items:
        lines.append("- None")
        return lines

    for item in items[:limit]:
        lines.append(f"- {item}")
    return lines


def render_macro_market_telegram(result: MacroMarketResult) -> str:
    signals = result.signals
    analysis = result.analysis
    summary = result.summary

    lines: list[str] = []
    lines.append("📌 Macro Market Brief")
    lines.append(
        f"Regime: {analysis.regime_label} | "
        f"Risk: {signals.macro_risk_tone} | "
        f"Crypto: {signals.crypto_momentum}"
    )
    lines.append(
        f"USD: {signals.dollar_tone} | "
        f"Rates: {signals.rates_tone} | "
        f"Equity: {signals.equity_tone}"
    )
    lines.append("")

    if summary.headline:
        lines.append(f"Headline: {summary.headline}")
        lines.append("")

    lines.extend(_render_lines("Drivers", analysis.top_drivers, limit=3))
    lines.append("")
    lines.extend(_render_lines("Risks", analysis.top_risks, limit=3))
    lines.append("")
    lines.extend(_render_lines("Watch", analysis.watch_items, limit=4))

    return "\n".join(lines).strip()