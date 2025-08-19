"""Core dataclasses matching JSON schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional


@dataclass(slots=True)
class RawFrame:
    schema: str
    venue: str
    channel: str
    stream: str
    payload: dict[str, Any]
    venue_ts: float
    recv_ts: float
    seq: Optional[int]
    checksum: Optional[str]
    staleness_ms: int
    connection_id: str
    trace_id: str
    size_bytes: int
    codec: str


@dataclass(slots=True)
class L2Level:
    px: float
    qty: float
    side: str


@dataclass(slots=True)
class Orderbook:
    ts: datetime
    asset: str
    venue: str
    seq: int
    checksum: str
    l2: List[L2Level]
    spread_bps: Optional[float] = None


@dataclass(slots=True)
class Trade:
    ts: datetime
    asset: str
    venue: str
    px: float
    qty: float
    side: str
    agg_id: Optional[str] = None


@dataclass(slots=True)
class Tick:
    ts: datetime
    asset: str
    venue: str
    bid: float
    ask: float
    mid: float
    last: float
    vol: float
    spread_bps: float
    staleness_ms: int


@dataclass(slots=True)
class VenueStatus:
    ts: datetime
    venue: str
    status: str
    api_latency_ms: Optional[float] = None
    rate_limit_rem: Optional[int] = None
    notes: Optional[str] = None
