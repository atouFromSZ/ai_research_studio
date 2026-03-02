from __future__ import annotations

from ai_research_studio.workflows.telegram_commands.router import route_telegram_command


def handle_incoming_telegram_text(text: str) -> str:
    return route_telegram_command(text)