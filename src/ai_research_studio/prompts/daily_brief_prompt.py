from typing import Any


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
            f"low={item['low_price']:.4f}, "
            f"volume={item['volume']:.4f}"
        )
    return "\n".join(lines)


def _build_news_prompt_block(news_items: list[dict[str, Any]]) -> str:
    if not news_items:
        return "News headlines:\n- No headlines available"

    lines = ["News headlines:"]
    for item in news_items[:8]:
        lines.append(f"- {item.get('title', 'Untitled')}")
    return "\n".join(lines)


def build_daily_brief_messages(
    major_snapshot: list[dict[str, Any]],
    watchlist_snapshot: list[dict[str, Any]],
    news_items: list[dict[str, Any]],
) -> list[dict[str, str]]:
    system_prompt = (
        "You are a concise crypto research assistant. "
        "Write a short daily market summary in Chinese. "
        "Use only the data explicitly provided by the user. "
        "Do not infer new price levels, breakouts, new highs, or volume comparisons unless they are directly supported by the provided numbers. "
        "Do not make up facts. "
        "If evidence is insufficient, say uncertainty clearly. "
        "Keep it to 3-4 sentences. "
        "Do not use markdown bullet points."
    )

    user_prompt = (
        "Please summarize strictly based on the following market snapshot and headlines. "
        "Do not add facts not present in the input.\n\n"
        + "\n\n".join(
            [
                _build_market_prompt_block("Major assets", major_snapshot),
                _build_market_prompt_block("Watchlist", watchlist_snapshot),
                _build_news_prompt_block(news_items),
            ]
        )
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]