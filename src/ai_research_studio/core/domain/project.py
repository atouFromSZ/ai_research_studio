from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from .common import BaseEvent


@dataclass
class ProjectBase:
    project_id: str
    project_name: str
    project_type: Literal["pre_tge", "post_tge"] = "pre_tge"
    tge_status: Literal["not_issued", "announced", "launched"] = "not_issued"

    ticker: Optional[str] = None
    ecosystem: Optional[str] = None
    category: Optional[str] = None
    official_website: Optional[str] = None
    official_x: Optional[str] = None
    founder_x: Optional[str] = None
    github_url: Optional[str] = None
    docs_url: Optional[str] = None


@dataclass
class ProjectEvent(BaseEvent):
    project_id: str = ""
    event_type: Literal[
        "official_announcement",
        "founder_statement",
        "product_update",
        "github_update",
        "partnership",
        "fundraising",
        "listing",
        "governance",
        "token_unlock",
        "onchain_transfer",
        "community_signal",
    ] = "official_announcement"
    signal_type: Literal["progress", "neutral", "risk", "hype", "anomaly"] = "neutral"
    signal_strength: Literal["low", "medium", "high"] = "medium"
    is_new_information: bool = True
    needs_followup: bool = False


@dataclass
class ProjectMarketSnapshot:
    project_id: str
    token_symbol: str
    price: Optional[float] = None
    market_cap: Optional[float] = None
    fdv: Optional[float] = None
    volume_24h: Optional[float] = None
    open_interest: Optional[float] = None
    funding_rate: Optional[float] = None
    liquidity: Optional[float] = None