from __future__ import annotations

from datetime import datetime

from ai_research_studio.core.domain.outputs import BriefOutput
from ai_research_studio.settings import settings
from ai_research_studio.shared.collectors.macro_market_data import (
    fetch_macro_market_snapshot,
)
from ai_research_studio.shared.collectors.market_data import fetch_market_snapshot
from ai_research_studio.shared.collectors.news_feed import fetch_rss_titles
from ai_research_studio.shared.renderers.markdown import format_market_snapshot_lines
from ai_research_studio.shared.storage.markdown_store import (
    get_latest_markdown_file,
    read_markdown,
    write_markdown,
)
from ai_research_studio.workflows.daily_brief.tasks import (
    build_macro_market_section,
    build_news_section,
    build_overview,
    build_rule_based_summary,
    build_summary_skeleton,
    try_generate_llm_summary,
)


def extract_markdown_section(content: str, heading: str) -> str | None:
    lines = content.splitlines()
    start_idx = None

    for i, line in enumerate(lines):
        if line.strip() == heading:
            start_idx = i + 1
            break

    if start_idx is None:
        return None

    collected: list[str] = []
    for line in lines[start_idx:]:
        if line.startswith("## "):
            break
        collected.append(line)

    text = "\n".join(collected).strip()
    return text or None


def safe_build_macro_market_section(
    *,
    crypto_market_items: list[dict] | None = None,
    macro_market_items: list[dict] | None = None,
    news_items: list[dict] | None = None,
    calendar_items: list[dict] | None = None,
    generated_at: str | None = None,
) -> str:
    """
    对 macro_market 引擎做容错包装，避免其异常影响 daily_brief 主链路。
    """
    try:
        return build_macro_market_section(
            crypto_market_items=crypto_market_items,
            macro_market_items=macro_market_items,
            news_items=news_items,
            calendar_items=calendar_items,
            generated_at=generated_at,
        )
    except Exception as exc:
        return "\n".join(
            [
                "## Macro Market",
                "",
                "- Macro market section unavailable.",
                f"- Error: `{type(exc).__name__}: {exc}`",
            ]
        )


def build_daily_brief_markdown() -> str:
    now = datetime.now()

    major_snapshot = fetch_market_snapshot(settings.major_symbol_list)
    watchlist_snapshot = fetch_market_snapshot(settings.watchlist_symbol_list)
    macro_market_items = fetch_macro_market_snapshot(settings.macro_symbol_list)

    reuters_items = fetch_rss_titles(settings.reuters_world_rss, settings.rss_item_limit)
    coindesk_items = fetch_rss_titles(settings.coindesk_rss, settings.rss_item_limit)
    all_news_items = reuters_items + coindesk_items

    overview_section = build_overview(major_snapshot, watchlist_snapshot)
    summary_section = build_summary_skeleton(major_snapshot, watchlist_snapshot, all_news_items)

    fallback_summary = build_rule_based_summary(major_snapshot, watchlist_snapshot, all_news_items)
    llm_summary = try_generate_llm_summary(major_snapshot, watchlist_snapshot, all_news_items)

    final_ai_summary = llm_summary or fallback_summary
    summary_source = "LLM" if llm_summary else "Rule-based fallback"

    major_section = format_market_snapshot_lines(major_snapshot)
    watchlist_section = format_market_snapshot_lines(watchlist_snapshot)
    news_section = build_news_section(all_news_items)

    macro_market_section = safe_build_macro_market_section(
        crypto_market_items=major_snapshot + watchlist_snapshot,
        macro_market_items=macro_market_items,
        news_items=all_news_items,
        calendar_items=None,
        generated_at=now.isoformat(),
    )

    markdown = f"""# Daily Brief

- Generated at: {now.strftime("%Y-%m-%d %H:%M:%S")}
- Project: {settings.project_name}

## Overview

{overview_section}

## Summary Skeleton

{summary_section}

## AI Summary

- Summary Source: **{summary_source}**

{final_ai_summary}

{macro_market_section}

## Major Assets

{major_section}

## Watchlist

{watchlist_section}

## Headlines by Category

{news_section}

## Notes

This report combines live Binance market data with classified public RSS headlines and a pluggable AI summary layer.

## Next Step

- Continue migrating old daily brief logic into the new foundation
- Remove legacy dependency
- Stabilize storage / llm / workflow boundaries
"""
    return markdown


def generate_daily_brief() -> BriefOutput:
    now = datetime.now()
    file_name = f"{now.strftime('%Y-%m-%d')}_daily_brief.md"
    output_path = settings.daily_reports_dir / file_name

    markdown = build_daily_brief_markdown()
    saved_path = write_markdown(output_path, markdown)

    return BriefOutput(
        brief_type="daily_brief_generation",
        engine_type="daily_brief",
        headline="日报已生成",
        key_points=[f"输出文件: {saved_path}"],
        source_refs=[str(saved_path)],
        generated_at=datetime.utcnow(),
    )


def view_latest_daily_brief() -> BriefOutput:
    latest = get_latest_markdown_file(settings.daily_reports_dir)
    if latest is None:
        return BriefOutput(
            brief_type="daily_brief_view",
            engine_type="daily_brief",
            headline="未找到日报",
            key_points=["当前 reports/daily/ 目录下没有日报文件。"],
        )

    content = read_markdown(latest)
    preview = content[:1200]

    return BriefOutput(
        brief_type="daily_brief_view",
        engine_type="daily_brief",
        headline="最新日报",
        key_points=[preview],
        source_refs=[str(latest)],
        generated_at=datetime.utcnow(),
    )


def summarize_latest_daily_brief() -> BriefOutput:
    latest = get_latest_markdown_file(settings.daily_reports_dir)
    if latest is None:
        return BriefOutput(
            brief_type="daily_brief_summary",
            engine_type="daily_brief",
            headline="未找到日报",
            key_points=["当前 reports/daily/ 目录下没有日报文件，无法总结。"],
        )

    content = read_markdown(latest)

    ai_summary = extract_markdown_section(content, "## AI Summary")
    overview = extract_markdown_section(content, "## Overview")
    summary_skeleton = extract_markdown_section(content, "## Summary Skeleton")

    key_points: list[str] = []

    if ai_summary:
        key_points.append(ai_summary[:1200])

    if overview:
        key_points.append("【Overview】\n" + overview[:500])

    if summary_skeleton:
        key_points.append("【Summary Skeleton】\n" + summary_skeleton[:500])

    if not key_points:
        key_points.append(content[:1200])

    return BriefOutput(
        brief_type="daily_brief_summary",
        engine_type="daily_brief",
        headline="最新日报总结",
        key_points=key_points,
        source_refs=[str(latest)],
        generated_at=datetime.utcnow(),
    )