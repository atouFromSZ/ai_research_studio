from datetime import datetime

from ai_research_studio.collectors.http_collector import fetch_market_snapshot
from ai_research_studio.collectors.news_collector import fetch_rss_titles
from ai_research_studio.outputs.markdown_writer import write_markdown
from ai_research_studio.settings import settings
from ai_research_studio.summarizers.llm_summary import maybe_generate_llm_summary
from ai_research_studio.summarizers.rule_based_summary import build_rule_based_summary
from ai_research_studio.utils.news_classifier import classify_news_items


def format_change(change: float) -> str:
    if change > 0:
        return f"🟢 {change:.2f}%"
    if change < 0:
        return f"🔴 {change:.2f}%"
    return f"⚪ {change:.2f}%"


def format_market_lines(snapshot: list[dict]) -> str:
    sorted_snapshot = sorted(snapshot, key=lambda x: x["price_change_percent"], reverse=True)
    lines: list[str] = []

    for item in sorted_snapshot:
        lines.append(
            "\n".join(
                [
                    f"### {item['symbol']}",
                    f"- Last Price: {item['last_price']:,.4f}",
                    f"- 24h Change: {format_change(item['price_change_percent'])}",
                    f"- 24h High: {item['high_price']:,.4f}",
                    f"- 24h Low: {item['low_price']:,.4f}",
                    f"- Volume: {item['volume']:,.4f}",
                    f"- Quote Volume: {item['quote_volume']:,.2f}",
                ]
            )
        )

    return "\n\n".join(lines)


def build_overview(major_snapshot: list[dict], watchlist_snapshot: list[dict]) -> str:
    combined = major_snapshot + watchlist_snapshot
    if not combined:
        return "- No market data available."

    sorted_by_change = sorted(combined, key=lambda x: x["price_change_percent"], reverse=True)
    strongest = sorted_by_change[0]
    weakest = sorted_by_change[-1]

    return "\n".join(
        [
            f"- Strongest asset today: **{strongest['symbol']}** ({format_change(strongest['price_change_percent'])})",
            f"- Lowest performer in tracked assets: **{weakest['symbol']}** ({format_change(weakest['price_change_percent'])})",
            f"- Total tracked symbols: **{len(combined)}**",
        ]
    )


def format_news_category_block(category: str, items: list[dict]) -> str:
    if not items:
        return f"### {category}\n- No items classified."

    lines = [f"### {category}"]
    for item in items:
        lines.append(f"- [{item['title']}]({item['link']})")
    return "\n".join(lines)


def build_news_section(all_news_items: list[dict]) -> str:
    grouped = classify_news_items(all_news_items)

    ordered_categories = [
        "Macro",
        "Policy / Regulation",
        "Tech / Protocol",
        "Market Structure",
        "Other",
    ]

    blocks = [format_news_category_block(category, grouped[category]) for category in ordered_categories]
    return "\n\n".join(blocks)


def build_summary_skeleton(
    major_snapshot: list[dict],
    watchlist_snapshot: list[dict],
    all_news_items: list[dict],
) -> str:
    combined = major_snapshot + watchlist_snapshot
    sorted_by_change = sorted(combined, key=lambda x: x["price_change_percent"], reverse=True)

    strongest = sorted_by_change[0]
    weakest = sorted_by_change[-1]

    grouped = classify_news_items(all_news_items)
    non_empty_categories = [name for name, items in grouped.items() if items]

    category_line = ", ".join(non_empty_categories) if non_empty_categories else "None"

    return "\n".join(
        [
            f"- Market leader today: **{strongest['symbol']}** ({format_change(strongest['price_change_percent'])})",
            f"- Market laggard today: **{weakest['symbol']}** ({format_change(weakest['price_change_percent'])})",
            f"- Active headline categories: **{category_line}**",
        ]
    )


def build_daily_brief_markdown() -> str:
    now = datetime.now()

    major_snapshot = fetch_market_snapshot(settings.major_symbol_list)
    watchlist_snapshot = fetch_market_snapshot(settings.watchlist_symbol_list)

    reuters_items = fetch_rss_titles(settings.reuters_world_rss, settings.rss_item_limit)
    coindesk_items = fetch_rss_titles(settings.coindesk_rss, settings.rss_item_limit)

    all_news_items = reuters_items + coindesk_items

    overview_section = build_overview(major_snapshot, watchlist_snapshot)
    summary_section = build_summary_skeleton(major_snapshot, watchlist_snapshot, all_news_items)

    fallback_summary = build_rule_based_summary(major_snapshot, watchlist_snapshot, all_news_items)
    llm_summary = maybe_generate_llm_summary(major_snapshot, watchlist_snapshot, all_news_items)

    final_ai_summary = llm_summary or fallback_summary
    summary_source = "LLM" if llm_summary else "Rule-based fallback"

    major_section = format_market_lines(major_snapshot)
    watchlist_section = format_market_lines(watchlist_snapshot)
    news_section = build_news_section(all_news_items)

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

## Major Assets

{major_section}

## Watchlist

{watchlist_section}

## Headlines by Category

{news_section}

## Notes

This report combines live Binance market data with classified public RSS headlines and a pluggable AI summary layer.

## Next Step

- Connect a real LLM provider via .env
- Add better macro source redundancy
- Refine headline classification rules
- Add scheduled automation
"""
    return markdown


def run_daily_brief() -> str:
    now = datetime.now()
    file_name = f"{now.strftime('%Y-%m-%d')}_daily_brief.md"
    output_path = settings.daily_reports_dir / file_name

    markdown = build_daily_brief_markdown()
    saved_path = write_markdown(output_path, markdown)
    return str(saved_path)