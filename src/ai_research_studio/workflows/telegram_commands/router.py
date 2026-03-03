from __future__ import annotations

from ai_research_studio.engines.macro_market.handlers.view_brief import (
    view_macro_market_brief,
)
from ai_research_studio.engines.project_watch.workflows.generate_project_brief import (
    generate_project_brief,
)
from ai_research_studio.shared.renderers.telegram import render_brief_output_for_telegram
from ai_research_studio.workflows.daily_brief.orchestrator import (
    generate_daily_brief,
    summarize_latest_daily_brief,
    view_latest_daily_brief,
)
from ai_research_studio.workflows.telegram_commands.intents import ParsedIntent


def parse_intent(text: str) -> ParsedIntent:
    text = text.strip()

    if text == "生成日报":
        return ParsedIntent(name="generate_daily_brief", raw_text=text)

    if text == "查看最新日报":
        return ParsedIntent(name="view_latest_daily_brief", raw_text=text)

    if text == "总结最新日报":
        return ParsedIntent(name="summarize_latest_daily_brief", raw_text=text)

    if text == "查看大行情简报":
        return ParsedIntent(name="view_macro_brief", raw_text=text)

    if text.startswith("查看项目 "):
        project_name = text.replace("查看项目 ", "", 1).strip()
        return ParsedIntent(name="view_project_status", raw_text=text, project_name=project_name)

    return ParsedIntent(name="unknown", raw_text=text)


def route_telegram_command(text: str) -> str:
    intent = parse_intent(text)

    try:
        if intent.name == "generate_daily_brief":
            result = generate_daily_brief()
            return render_brief_output_for_telegram(result)

        if intent.name == "view_latest_daily_brief":
            result = view_latest_daily_brief()
            return render_brief_output_for_telegram(result)

        if intent.name == "summarize_latest_daily_brief":
            result = summarize_latest_daily_brief()
            return render_brief_output_for_telegram(result)

        if intent.name == "view_macro_brief":
            result = view_macro_market_brief()
            return render_brief_output_for_telegram(result)

        if intent.name == "view_project_status":
            project = intent.project_name or "未知项目"
            result = generate_project_brief(project)
            return render_brief_output_for_telegram(result)

        return (
            "暂不支持这个命令。\n\n"
            "当前可用命令：\n"
            "- 生成日报\n"
            "- 查看最新日报\n"
            "- 总结最新日报\n"
            "- 查看大行情简报\n"
            "- 查看项目 <项目名>"
        )
    except Exception as e:
        return (
            "命令执行失败。\n\n"
            f"命令：{text}\n"
            f"错误类型：{type(e).__name__}\n"
            f"错误信息：{str(e)}"
        )