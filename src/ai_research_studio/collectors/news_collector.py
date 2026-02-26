from typing import Any

import feedparser


def fetch_rss_titles(feed_url: str, limit: int = 5) -> list[dict[str, Any]]:
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