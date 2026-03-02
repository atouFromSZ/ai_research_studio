from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BriefOutput:
    brief_type: str
    engine_type: str
    headline: str
    key_points: list[str] = field(default_factory=list)
    risk_points: list[str] = field(default_factory=list)
    followup_points: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)