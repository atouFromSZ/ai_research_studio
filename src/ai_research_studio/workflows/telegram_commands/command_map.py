from __future__ import annotations

from ai_research_studio.workflows.daily_brief.orchestrator import (
    generate_daily_brief,
    view_latest_daily_brief,
)


COMMAND_MAP = {
    "生成日报": generate_daily_brief,
    "查看最新日报": view_latest_daily_brief,
}