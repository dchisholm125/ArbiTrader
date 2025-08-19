"""Coinbase public WebSocket connector."""

from __future__ import annotations

import json
import time
from datetime import datetime
from typing import Any, Dict

from base_connector import BaseConnector

from crypto_ensemble.core.errors import SCHEMA_INVALID, CEMError
from crypto_ensemble.core.validators import validate_rawframe_v2


class CoinbaseConnector(BaseConnector):
    """Connector for Coinbase public WebSocket feeds."""

    venue = "coinbase"

    def __init__(self, publisher: Any, config: Dict[str, Any]) -> None:
        super().__init__(publisher)
        self.config = config

    @staticmethod
    def _iso_to_epoch(ts: str) -> float:
        """Convert an ISO8601 timestamp to epoch seconds."""
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()

    def _size_bytes(self, payload: Any) -> int:
        """Return the byte size of the payload."""
        return len(json.dumps(payload).encode())

    def _trace_id(self, recv_ts: float) -> str:  # pragma: no cover - simple factory
        return str(int(recv_ts))

    def _raw_frame(
        self,
        *,
        channel: str,
        stream: str,
        payload: Any,
        venue_ts: float,
        seq: int | None = None,
        checksum: str | None = None,
    ) -> Dict[str, Any]:
        recv_ts = time.time()
        data: Dict[str, Any] = {
            "schema": "RawFrame.v2",
            "venue": self.venue,
            "channel": channel,
            "stream": stream,
            "payload": payload,
            "venue_ts": venue_ts,
            "recv_ts": recv_ts,
            "seq": seq,
            "checksum": checksum,
            "staleness_ms": int(round((recv_ts - venue_ts) * 1000)),
            "connection_id": self._connection_id,
            "trace_id": self._trace_id(recv_ts),
            "size_bytes": self._size_bytes(payload),
            "codec": "none",
        }
        validate_rawframe_v2(data)
        return data

    def parse_message(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a Coinbase WebSocket message into a RawFrame."""
        msg_type = msg.get("type")
        product = msg.get("product_id", "")
        if msg_type == "match":
            channel = "trades.tape"
            stream = f"matches:{product}"
            venue_ts = self._iso_to_epoch(msg["time"])
            seq = int(msg["sequence"])
        elif msg_type in {"snapshot", "l2update"}:
            channel = "orderbook.l2"
            stream = f"level2:{product}"
            time_field = msg.get("time")
            venue_ts = self._iso_to_epoch(time_field) if time_field else time.time()
            seq = None
        else:
            raise CEMError(SCHEMA_INVALID, f"unknown type {msg_type}")
        return self._raw_frame(
            channel=channel, stream=stream, payload=msg, venue_ts=venue_ts, seq=seq
        )

    async def run(self) -> None:  # pragma: no cover - network interaction
        raise NotImplementedError
