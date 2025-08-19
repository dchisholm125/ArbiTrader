"""Heartbeat emitter utility."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional


class Heartbeat:
    """Emit heartbeat dictionaries via a callback."""

    def __init__(
        self,
        emit: Callable[[Dict[str, Any]], None],
        *,
        latency_ms_p95: Optional[float] = None,
        reconnects_total: Optional[int] = None,
    ) -> None:
        """Create a heartbeat emitter with optional metrics."""
        self.emit = emit
        self.latency_ms_p95 = latency_ms_p95
        self.reconnects_total = reconnects_total

    def set_latency_p95(self, value: float) -> None:
        """Set the 95th percentile latency metric."""
        self.latency_ms_p95 = value

    def set_reconnects_total(self, value: int) -> None:
        """Set the reconnect counter."""
        self.reconnects_total = value

    def tick(self, module: str, version: str) -> Dict[str, Any]:
        """Emit a heartbeat and return the payload."""
        hb: Dict[str, Any] = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "module": module,
            "version": version,
            "ok": True,
        }
        if self.latency_ms_p95 is not None:
            hb["latency_ms_p95"] = self.latency_ms_p95
        if self.reconnects_total is not None:
            hb["reconnects_total"] = self.reconnects_total
        self.emit(hb)
        return hb
