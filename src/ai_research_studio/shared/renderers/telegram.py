from __future__ import annotations

from ai_research_studio.core.domain.outputs import BriefOutput


def render_brief_output_for_telegram(output: BriefOutput) -> str:
    parts: list[str] = [f"**{output.headline}**"]

    if output.key_points:
        parts.append("\n【要点】")
        parts.extend([f"- {item}" for item in output.key_points])

    if output.risk_points:
        parts.append("\n【风险】")
        parts.extend([f"- {item}" for item in output.risk_points])

    if output.followup_points:
        parts.append("\n【后续关注】")
        parts.extend([f"- {item}" for item in output.followup_points])

    if output.source_refs:
        parts.append("\n【来源/文件】")
        parts.extend([f"- {item}" for item in output.source_refs])

    return "\n".join(parts)