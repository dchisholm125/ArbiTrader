"""Latency probe for RPC endpoints."""

from __future__ import annotations

import time
from typing import Awaitable, Callable, Dict, Optional


class LatencyProbe:
    """Measure round-trip time for a callable."""

    def __init__(self, clock: Optional[Callable[[], float]] = None) -> None:
        """Initialize the probe with an optional clock."""
        self.clock = clock or time.perf_counter

    async def measure(
        self, venue: str, rpc: Callable[[], Awaitable[None]]
    ) -> Dict[str, float]:
        """Execute the RPC and return rtt in ms."""
        start = self.clock()
        await rpc()
        rtt = (self.clock() - start) * 1000
        return {"venue": venue, "rtt_ms": rtt}
