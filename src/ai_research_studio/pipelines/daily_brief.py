from datetime import datetime

from ai_research_studio.collectors.http_collector import fetch_market_snapshot
from ai_research_studio.outputs.markdown_writer import write_markdown
from ai_research_studio.settings import settings


def format_market_lines(snapshot: list[dict]) -> str:
    lines: list[str] = []

    for item in snapshot:
        lines.append(
            "\n".join(
                [
                    f"### {item['symbol']}",
                    f"- Last Price: {item['last_price']:,.4f}",
                    f"- 24h Change: {item['price_change_percent']:.2f}%",
                    f"- 24h High: {item['high_price']:,.4f}",
                    f"- 24h Low: {item['low_price']:,.4f}",
                    f"- Volume: {item['volume']:,.4f}",
                    f"- Quote Volume: {item['quote_volume']:,.2f}",
                ]
            )
        )

    return "\n\n".join(lines)


def build_daily_brief_markdown() -> str:
    now = datetime.now()
    snapshot = fetch_market_snapshot(settings.symbol_list)
    market_section = format_market_lines(snapshot)

    markdown = f"""# Daily Brief

- Generated at: {now.strftime("%Y-%m-%d %H:%M:%S")}
- Project: {settings.project_name}

## Market Snapshot

{market_section}

## Summary

This report is generated from live Binance market data for the selected watchlist.

## Next Step

- Add more symbols and watchlists
- Add news and macro sections
- Add LLM summarization
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