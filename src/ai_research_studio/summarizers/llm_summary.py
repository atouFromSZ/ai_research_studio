from typing import Any

from ai_research_studio.llm.openai_compatible import build_llm_client
from ai_research_studio.prompts.daily_brief_prompt import build_daily_brief_messages
from ai_research_studio.settings import settings


def maybe_generate_llm_summary(
    major_snapshot: list[dict[str, Any]],
    watchlist_snapshot: list[dict[str, Any]],
    news_items: list[dict[str, Any]],
) -> str | None:
    if not settings.use_llm_summary:
        return None

    client = build_llm_client()
    if client is None:
        return None

    messages = build_daily_brief_messages(
        major_snapshot=major_snapshot,
        watchlist_snapshot=watchlist_snapshot,
        news_items=news_items,
    )
    return client.generate(messages)