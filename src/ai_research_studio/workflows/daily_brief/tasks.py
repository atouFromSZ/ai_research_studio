from __future__ import annotations

from ai_research_studio.engines.macro_market.service import run_macro_market_brief
from ai_research_studio.shared.llm.daily_brief_summary import (
    maybe_generate_daily_brief_llm_summary,
)
from ai_research_studio.shared.renderers.markdown import format_price_change
from ai_research_studio.utils.news_classifier import classify_news_items


def build_overview(major_snapshot: list[dict], watchlist_snapshot: list[dict]) -> str:
    combined = major_snapshot + watchlist_snapshot
    if not combined:
        return "- No market data available."

    sorted_by_change = sorted(
        combined,
        key=lambda x: x["price_change_percent"],
        reverse=True,
    )
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

    blocks = [
        format_news_category_block(category, grouped[category])
        for category in ordered_categories
    ]
    return "\n\n".join(blocks)


def build_summary_skeleton(
    major_snapshot: list[dict],
    watchlist_snapshot: list[dict],
    all_news_items: list[dict],
) -> str:
    combined = major_snapshot + watchlist_snapshot
    if not combined:
        return "- No market data available.\n- No news categories available."

    sorted_by_change = sorted(
        combined,
        key=lambda x: x["price_change_percent"],
        reverse=True,
    )
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

    sorted_by_change = sorted(
        combined,
        key=lambda x: x["price_change_percent"],
        reverse=True,
    )
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


def _normalize_macro_market_markdown_for_daily_brief(markdown_text: str) -> str:
    """
    macro_market 引擎默认输出以 '# Macro Market' 开头。
    接入 daily_brief 时：
    1. 将主标题下调为 '## Macro Market'
    2. 将内部标题整体下调一级，避免和日报主层级冲突
    """
    if not markdown_text.strip():
        return "## Macro Market\n- No macro market content available."

    lines = markdown_text.splitlines()
    if not lines:
        return "## Macro Market\n- No macro market content available."

    normalized_lines: list[str] = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        if i == 0 and stripped == "# Macro Market":
            normalized_lines.append("## Macro Market")
            continue

        if stripped.startswith("### "):
            normalized_lines.append(line.replace("### ", "#### ", 1))
            continue

        if stripped.startswith("## "):
            normalized_lines.append(line.replace("## ", "### ", 1))
            continue

        normalized_lines.append(line)

    return "\n".join(normalized_lines).strip()

def build_macro_market_section(
    *,
    crypto_market_items: list[dict] | None = None,
    macro_market_items: list[dict] | None = None,
    news_items: list[dict] | None = None,
    calendar_items: list[dict] | None = None,
    generated_at: str | None = None,
) -> str:
    """
    供 daily_brief 调用的 macro_market 接入点。

    这里不在日报层重复做宏观分析，而是直接调用 macro_market service，
    拿回该引擎自己的 markdown 输出，再做日报层级归一化。
    """
    result = run_macro_market_brief(
        crypto_market_items=crypto_market_items,
        macro_market_items=macro_market_items,
        news_items=news_items,
        calendar_items=calendar_items,
        generated_at=generated_at,
    )
    return _normalize_macro_market_markdown_for_daily_brief(result.markdown)