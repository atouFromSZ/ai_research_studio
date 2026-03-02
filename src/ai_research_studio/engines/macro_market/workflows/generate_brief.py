from __future__ import annotations

from datetime import datetime

from ai_research_studio.core.domain.outputs import BriefOutput


def generate_macro_brief() -> BriefOutput:
    return BriefOutput(
        brief_type="macro_market_brief",
        engine_type="macro_market",
        headline="大行情简报（占位版）",
        key_points=[
            "当前大行情引擎骨架已建立。",
            "下一步将接入 BTC / ETH 的事件收集、状态分析与摘要生成。",
        ],
        generated_at=datetime.utcnow(),
    )