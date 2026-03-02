from __future__ import annotations

from ai_research_studio.shared.llm.daily_brief_summary import (
    maybe_generate_daily_brief_llm_summary,
)
from ai_research_studio.shared.renderers.markdown import format_price_change
from ai_research_studio.utils.news_classifier import classify_news_items


def build_overview(major_snapshot: list[dict], watchlist_snapshot: list[dict]) -> str:
    combined = major_snapshot + watchlist_snapshot
    if not combined:
        return "- No market data available."

    sorted_by_change = sorted(combined, key=lambda x: x["price_change_percent"], reverse=True)
    strongest = sorted_by_change[0]
    weakest = sorted_by_change[-1]

    return "\n".join(
        [
            f"- Strongest asset today: **{strongest['symbol']}** ({format_price_change(strongest['price_change_percent'])})",
            f"- Lowest performer in tracked assets: **{weakest['symbol']}** ({format_price_change(weakest['price_change_percent'])})",
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
    if not combined:
        return "- No market data available.\n- No news categories available."

    sorted_by_change = sorted(combined, key=lambda x: x["price_change_percent"], reverse=True)

    strongest = sorted_by_change[0]
    weakest = sorted_by_change[-1]

    grouped = classify_news_items(all_news_items)
    non_empty_categories = [name for name, items in grouped.items() if items]

    category_line = ", ".join(non_empty_categories) if non_empty_categories else "None"

    return "\n".join(
        [
            f"- Market leader today: **{strongest['symbol']}** ({format_price_change(strongest['price_change_percent'])})",
            f"- Market laggard today: **{weakest['symbol']}** ({format_price_change(weakest['price_change_percent'])})",
            f"- Active headline categories: **{category_line}**",
        ]
    )


def format_change_label(change: float) -> str:
    if change > 0:
        return f"上涨 {change:.2f}%"
    if change < 0:
        return f"下跌 {abs(change):.2f}%"
    return "基本持平"


def build_rule_based_summary(
    major_snapshot: list[dict],
    watchlist_snapshot: list[dict],
    all_news_items: list[dict],
) -> str:
    combined = major_snapshot + watchlist_snapshot

    if not combined:
        return "当前没有可用市场数据，暂时无法生成摘要。"

    sorted_by_change = sorted(combined, key=lambda x: x["price_change_percent"], reverse=True)
    strongest = sorted_by_change[0]
    weakest = sorted_by_change[-1]

    grouped = classify_news_items(all_news_items)
    active_categories = [name for name, items in grouped.items() if items]

    if active_categories:
        category_text = "、".join(active_categories)
    else:
        category_text = "暂无明显新闻主题"

    summary = (
        f"当前追踪资产中，表现最强的是 {strongest['symbol']}，"
        f"{format_change_label(strongest['price_change_percent'])}；"
        f"表现最弱的是 {weakest['symbol']}，"
        f"{format_change_label(weakest['price_change_percent'])}。"
        f"今日新闻主题主要集中在：{category_text}。"
    )

    return summary


def try_generate_llm_summary(
    major_snapshot: list[dict],
    watchlist_snapshot: list[dict],
    all_news_items: list[dict],
) -> str | None:
    return maybe_generate_daily_brief_llm_summary(
        major_snapshot=major_snapshot,
        watchlist_snapshot=watchlist_snapshot,
        news_items=all_news_items,
    )