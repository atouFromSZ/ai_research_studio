from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .common import BaseEvent


@dataclass
class MacroEvent(BaseEvent):
    asset_scope: Literal["btc", "eth", "both", "market_wide"] = "market_wide"
    event_type: Literal[
        "macro",
        "regulation",
        "etf",
        "flow",
        "derivatives",
        "onchain",
        "risk_event",
    ] = "macro"
    impact_direction: Literal["bullish", "bearish", "neutral", "mixed"] = "neutral"
    impact_level: Literal["low", "medium", "high", "critical"] = "medium"
    impact_horizon: Literal["intraday", "short_term", "medium_term"] = "short_term"
    affects_btc: bool = True
    affects_eth: bool = True