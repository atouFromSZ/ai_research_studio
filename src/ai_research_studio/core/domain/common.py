from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class BaseEvent:
    id: str
    engine_type: str
    source_type: str
    source_name: str
    title: str
    raw_text: str
    collected_at: datetime

    source_url: Optional[str] = None
    summary: Optional[str] = None
    event_time: Optional[datetime] = None
    tags: list[str] = field(default_factory=list)
    importance_score: Optional[float] = None
    confidence_score: Optional[float] = None