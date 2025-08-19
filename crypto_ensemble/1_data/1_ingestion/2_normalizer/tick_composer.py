"""Tick composer from orderbooks and trades."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from crypto_ensemble.core.errors import SCHEMA_INVALID, UPSTREAM_STALE, CEMError
from crypto_ensemble.core.validators import validate_tick_v1

Key = Tuple[str, str]


class TickComposer:
    """Compose ticks per asset and venue."""

    def __init__(self, staleness_ms: int = 1000) -> None:
        self.staleness_ms = staleness_ms
        self._obs: Dict[Key, dict[str, Any]] = {}
        self._trades: Dict[Key, dict[str, Any]] = {}

    def update_orderbook(self, ob: dict[str, Any]) -> None:
        """Update latest orderbook."""
        key: Key = (ob["asset"], ob["venue"])
        self._obs[key] = ob

    def update_trade(self, trade: dict[str, Any]) -> None:
        """Update latest trade."""
        key: Key = (trade["asset"], trade["venue"])
        self._trades[key] = trade

    def maybe_emit_tick(self, asset: str, venue: str) -> dict[str, Any] | None:
        """Emit Tick.v1 if both orderbook and trade are present."""
        key: Key = (asset, venue)
        ob = self._obs.get(key)
        tr = self._trades.get(key)
        if not ob or not tr:
            return None
        bid = next((lvl["px"] for lvl in ob["l2"] if lvl["side"] == "bid"), 0.0)
        ask = next((lvl["px"] for lvl in ob["l2"] if lvl["side"] == "ask"), 0.0)
        mid = (bid + ask) / 2 if bid and ask else 0.0
        now_ms = int(time.time() * 1000)
        ob_ts = int(datetime.fromisoformat(ob["ts"]).timestamp() * 1000)
        tr_ts = int(datetime.fromisoformat(tr["ts"]).timestamp() * 1000)
        staleness_ms = now_ms - max(ob_ts, tr_ts)
        if staleness_ms > self.staleness_ms:
            raise CEMError(UPSTREAM_STALE, "tick stale")
        tick = {
            "ts": datetime.fromtimestamp(now_ms / 1000, tz=timezone.utc).isoformat(),
            "asset": asset,
            "venue": venue,
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "last": tr["px"],
            "vol": tr["qty"],
            "spread_bps": (ask - bid) / mid * 10000 if mid else 0.0,
            "staleness_ms": staleness_ms,
        }
        try:
            validate_tick_v1(tick)
        except Exception as exc:  # pragma: no cover - fastjsonschema detail
            raise CEMError(SCHEMA_INVALID, str(exc)) from exc
        return tick
