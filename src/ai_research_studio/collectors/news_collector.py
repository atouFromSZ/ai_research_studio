from typing import Any

import feedparser


def fetch_rss_titles(feed_url: str, limit: int = 5) -> list[dict[str, Any]]:
    """从指定 RSS 源抓取最新若干条标题，统一抽取为简单 dict。"""
    feed = feedparser.parse(feed_url)
    items: list[dict[str, Any]] = []

    for entry in feed.entries[:limit]:
        items.append(
            {
                "title": getattr(entry, "title", "Untitled"),
                "link": getattr(entry, "link", ""),
                "published": getattr(entry, "published", "N/A"),
            }
        )

    return items