from __future__ import annotations

from datetime import datetime

from ai_research_studio.core.domain.outputs import BriefOutput


def generate_project_brief(project_name: str) -> BriefOutput:
    return BriefOutput(
        brief_type="project_watch_brief",
        engine_type="project_watch",
        headline=f"{project_name} 项目简报（占位版）",
        key_points=[
            f"项目：{project_name}",
            "当前单项目引擎骨架已建立。",
            "下一步将接入项目基础信息、事件收集、状态判断与摘要生成。",
        ],
        generated_at=datetime.utcnow(),
    )