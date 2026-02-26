from typing import Any

import requests

from ai_research_studio.settings import settings


def _build_market_prompt_block(title: str, snapshot: list[dict[str, Any]]) -> str:
    if not snapshot:
        return f"{title}: no data"

    lines = [title]
    for item in snapshot:
        lines.append(
            f"- {item['symbol']}: "
            f"last={item['last_price']:.4f}, "
            f"change_24h={item['price_change_percent']:.2f}%, "
            f"high={item['high_price']:.4f}, "
            f"low={item['low_price']:.4f}"
        )
    return "\n".join(lines)


def _build_news_prompt_block(news_items: list[dict[str, Any]]) -> str:
    if not news_items:
        return "News headlines:\n- No headlines available"

    lines = ["News headlines:"]
    for item in news_items[:8]:
        lines.append(f"- {item.get('title', 'Untitled')}")
    return "\n".join(lines)


def build_llm_messages(
    major_snapshot: list[dict[str, Any]],
    watchlist_snapshot: list[dict[str, Any]],
    news_items: list[dict[str, Any]],
) -> list[dict[str, str]]:
    system_prompt = (
        "You are a concise crypto research assistant. "
        "Write a short daily market summary in Chinese. "
        "Focus on: market strength/weakness, major themes in headlines, and one practical observation. "
        "Keep it to 3-5 sentences. Do not use markdown bullet points."
    )

    user_prompt = "\n\n".join(
        [
            _build_market_prompt_block("Major assets", major_snapshot),
            _build_market_prompt_block("Watchlist", watchlist_snapshot),
            _build_news_prompt_block(news_items),
        ]
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def maybe_generate_llm_summary(
    major_snapshot: list[dict[str, Any]],
    watchlist_snapshot: list[dict[str, Any]],
    news_items: list[dict[str, Any]],
) -> str | None:
    if not settings.use_llm_summary:
        return None

    if not settings.openai_api_key:
        return None

    url = settings.openai_base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openai_model,
        "messages": build_llm_messages(major_snapshot, watchlist_snapshot, news_items),
        "temperature": 0.2,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=settings.llm_timeout)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"].strip()
        return content or None
    except Exception:
        return None