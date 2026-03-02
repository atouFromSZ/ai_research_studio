from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


IntentName = Literal[
    "generate_daily_brief",
    "view_latest_daily_brief",
    "summarize_latest_daily_brief",
    "view_macro_brief",
    "view_project_status",
    "unknown",
]


@dataclass
class ParsedIntent:
    name: IntentName
    raw_text: str
    project_name: Optional[str] = None