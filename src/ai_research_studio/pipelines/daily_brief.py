from datetime import datetime

from ai_research_studio.collectors.http_collector import fetch_market_snapshot
from ai_research_studio.collectors.news_collector import fetch_rss_titles
from ai_research_studio.outputs.markdown_writer import write_markdown
from ai_research_studio.settings import settings


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


def format_news_block(title: str, items: list[dict]) -> str:
    if not items:
        return f"### {title}\n- No items available."

    lines = [f"### {title}"]
    for item in items:
        lines.append(f"- [{item['title']}]({item['link']})")
    return "\n".join(lines)


def build_daily_brief_markdown() -> str:
    now = datetime.now()

    major_snapshot = fetch_market_snapshot(settings.major_symbol_list)
    watchlist_snapshot = fetch_market_snapshot(settings.watchlist_symbol_list)

    reuters_items = fetch_rss_titles(settings.reuters_world_rss, settings.rss_item_limit)
    coindesk_items = fetch_rss_titles(settings.coindesk_rss, settings.rss_item_limit)

    overview_section = build_overview(major_snapshot, watchlist_snapshot)
    major_section = format_market_lines(major_snapshot)
    watchlist_section = format_market_lines(watchlist_snapshot)

    macro_news_section = "\n\n".join(
        [
            format_news_block("Reuters World", reuters_items),
            format_news_block("CoinDesk", coindesk_items),
        ]
    )

    markdown = f"""# Daily Brief

- Generated at: {now.strftime("%Y-%m-%d %H:%M:%S")}
- Project: {settings.project_name}

## Overview

{overview_section}

## Major Assets

{major_section}

## Watchlist

{watchlist_section}

## Macro / Headlines

{macro_news_section}

## Notes

This report combines live Binance market data with public RSS headlines.

## Next Step

- Add more curated macro and crypto sources
- Add headline classification
- Add LLM-generated summary
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