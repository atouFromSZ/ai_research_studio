from __future__ import annotations

from datetime import datetime

from ai_research_studio.core.domain.outputs import BriefOutput
from ai_research_studio.engines.macro_market.service import run_macro_market_brief
from ai_research_studio.settings import settings
from ai_research_studio.shared.collectors.macro_market_data import fetch_macro_market_snapshot
from ai_research_studio.shared.collectors.market_data import fetch_market_snapshot
from ai_research_studio.shared.collectors.news_feed import fetch_rss_titles
from ai_research_studio.shared.storage.markdown_store import (
    get_latest_markdown_file,
    read_markdown,
)


def _build_block(title: str, items: list[str], *, limit: int) -> str:
    if not items:
        return f"【{title}】\n- None"

    lines = [f"【{title}】"]
    for item in items[:limit]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _extract_markdown_section(content: str, heading: str) -> str | None:
    lines = content.splitlines()
    start_idx = None

    for i, line in enumerate(lines):
        if line.strip() == heading:
            start_idx = i
            break

    if start_idx is None:
        return None

    collected: list[str] = []
    for line in lines[start_idx:]:
        if line.startswith("## ") and line.strip() != heading and collected:
            break
        collected.append(line)

    text = "\n".join(collected).strip()
    return text or None


def _build_realtime_macro_brief() -> BriefOutput:
    now = datetime.now()

    major_snapshot = fetch_market_snapshot(settings.major_symbol_list)
    watchlist_snapshot = fetch_market_snapshot(settings.watchlist_symbol_list)
    macro_market_items = fetch_macro_market_snapshot(settings.macro_symbol_list)

    reuters_items = fetch_rss_titles(settings.reuters_world_rss, settings.rss_item_limit)
    coindesk_items = fetch_rss_titles(settings.coindesk_rss, settings.rss_item_limit)
    all_news_items = reuters_items + coindesk_items

    result = run_macro_market_brief(
        crypto_market_items=major_snapshot + watchlist_snapshot,
        macro_market_items=macro_market_items,
        news_items=all_news_items,
        calendar_items=None,
        generated_at=now.isoformat(),
    )

    key_points: list[str] = []

    key_points.append(
        "\n".join(
            [
                f"Regime: {result.analysis.regime_label}",
                f"Risk Tone: {result.signals.macro_risk_tone}",
                f"Crypto Momentum: {result.signals.crypto_momentum}",
                f"Dollar Tone: {result.signals.dollar_tone}",
                f"Rates Tone: {result.signals.rates_tone}",
                f"Equity Tone: {result.signals.equity_tone}",
                f"Confidence: {result.signals.confidence:.2f}",
            ]
        )
    )

    if result.summary.headline:
        key_points.append(f"【Headline】\n{result.summary.headline}")

    if result.summary.summary:
        key_points.append(f"【Summary】\n{result.summary.summary}")

    key_points.append(_build_block("Top Drivers", result.analysis.top_drivers, limit=3))
    key_points.append(_build_block("Top Risks", result.analysis.top_risks, limit=3))
    key_points.append(_build_block("Watch Items", result.analysis.watch_items, limit=4))

    return BriefOutput(
        brief_type="macro_market_view",
        engine_type="macro_market",
        headline="大行情简报",
        key_points=key_points,
        generated_at=datetime.utcnow(),
    )


def _build_fallback_macro_brief_from_latest_daily() -> BriefOutput:
    latest = get_latest_markdown_file(settings.daily_reports_dir)
    if latest is None:
        return BriefOutput(
            brief_type="macro_market_view",
            engine_type="macro_market",
            headline="大行情简报（回退）",
            key_points=["未找到最近日报，且实时行情抓取失败。"],
            generated_at=datetime.utcnow(),
        )

    content = read_markdown(latest)
    macro_section = _extract_markdown_section(content, "## Macro Market")

    if not macro_section:
        return BriefOutput(
            brief_type="macro_market_view",
            engine_type="macro_market",
            headline="大行情简报（回退）",
            key_points=["最近日报中未找到 Macro Market 段。"],
            source_refs=[str(latest)],
            generated_at=datetime.utcnow(),
        )

    return BriefOutput(
        brief_type="macro_market_view",
        engine_type="macro_market",
        headline="大行情简报（来自最近日报回退）",
        key_points=[macro_section[:3500]],
        source_refs=[str(latest)],
        generated_at=datetime.utcnow(),
    )


def view_macro_market_brief() -> BriefOutput:
    try:
        return _build_realtime_macro_brief()
    except Exception:
        return _build_fallback_macro_brief_from_latest_daily()