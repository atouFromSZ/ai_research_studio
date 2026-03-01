id="6l5m1u"
from typing import Any


# 简单基于关键词的新闻分类规则，可根据需要继续扩展或微调。
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Macro": [
        "fed",
        "inflation",
        "cpi",
        "pce",
        "treasury",
        "yield",
        "recession",
        "economy",
        "economic",
        "tariff",
        "jobs",
        "payrolls",
        "rates",
        "rate cut",
        "rate hike",
    ],
    "Policy / Regulation": [
        "sec",
        "etf",
        "regulation",
        "regulatory",
        "congress",
        "senate",
        "house",
        "bill",
        "law",
        "policy",
        "pension",
        "compliance",
        "approval",
    ],
    "Tech / Protocol": [
        "ethereum",
        "solana",
        "bitcoin upgrade",
        "protocol",
        "foundation",
        "roadmap",
        "validator",
        "staking",
        "upgrade",
        "finality",
        "rollup",
        "network",
    ],
    "Market Structure": [
        "options",
        "trader",
        "traders",
        "flows",
        "volatility",
        "market",
        "bounce",
        "liquidation",
        "volume",
        "funding",
        "open interest",
        "oi",
    ],
}


def classify_headline(title: str) -> str:
    """根据标题中是否包含关键词，把新闻粗略映射到一个主题类别。"""
    normalized = title.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return category

    return "Other"


def classify_news_items(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """去重后按类别聚合新闻条目，返回按类别分组的字典。"""
    grouped: dict[str, list[dict[str, Any]]] = {
        "Macro": [],
        "Policy / Regulation": [],
        "Tech / Protocol": [],
        "Market Structure": [],
        "Other": [],
    }

    seen_titles: set[str] = set()

    for item in items:
        title = item.get("title", "").strip()
        if not title:
            continue

        normalized_title = title.lower()
        if normalized_title in seen_titles:
            continue
        seen_titles.add(normalized_title)

        category = classify_headline(title)
        grouped[category].append(item)

    return grouped