from ai_research_studio.utils.news_classifier import classify_news_items


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