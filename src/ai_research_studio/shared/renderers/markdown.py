from __future__ import annotations


def format_price_change(change: float) -> str:
    if change > 0:
        return f"🟢 {change:.2f}%"
    if change < 0:
        return f"🔴 {change:.2f}%"
    return f"⚪ {change:.2f}%"


def format_market_snapshot_lines(snapshot: list[dict]) -> str:
    sorted_snapshot = sorted(
        snapshot,
        key=lambda x: x["price_change_percent"],
        reverse=True,
    )
    lines: list[str] = []

    for item in sorted_snapshot:
        lines.append(
            "\n".join(
                [
                    f"### {item['symbol']}",
                    f"- Last Price: {item['last_price']:,.4f}",
                    f"- 24h Change: {format_price_change(item['price_change_percent'])}",
                    f"- 24h High: {item['high_price']:,.4f}",
                    f"- 24h Low: {item['low_price']:,.4f}",
                    f"- Volume: {item['volume']:,.4f}",
                    f"- Quote Volume: {item['quote_volume']:,.2f}",
                ]
            )
        )

    return "\n\n".join(lines)