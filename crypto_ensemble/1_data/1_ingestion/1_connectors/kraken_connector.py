"""Kraken public WebSocket connector."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from base_connector import BaseConnector

from crypto_ensemble.core.errors import SCHEMA_INVALID, CEMError
from crypto_ensemble.core.validators import validate_rawframe_v2


class KrakenConnector(BaseConnector):
    """Connector for Kraken public WebSocket feeds."""

    venue = "kraken"

    def __init__(self, publisher: Any, config: Dict[str, Any]) -> None:
        super().__init__(publisher)
        self.config = config

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

    def parse_message(self, msg: List[Any]) -> Dict[str, Any]:
        """Parse a Kraken WebSocket message into a RawFrame."""
        if len(msg) < 4:
            raise CEMError(SCHEMA_INVALID, "unexpected message shape")
        channel_name = msg[2]
        pair = msg[3]
        if channel_name.startswith("book-"):
            channel = "orderbook.l2"
            stream = f"{channel_name}:{pair}"
            book = msg[1]
            timestamps: List[float] = []
            for key in ("as", "bs", "a", "b"):
                for item in book.get(key, []):
                    timestamps.append(float(item[2]))
            venue_ts = max(timestamps) if timestamps else time.time()
        elif channel_name == "trade":
            channel = "trades.tape"
            stream = f"trade:{pair}"
            trades = msg[1]
            venue_ts = max(float(t[2]) for t in trades)
        else:
            raise CEMError(SCHEMA_INVALID, f"unknown channel {channel_name}")
        return self._raw_frame(
            channel=channel, stream=stream, payload=msg, venue_ts=venue_ts
        )

    async def run(self) -> None:  # pragma: no cover - network interaction
        raise NotImplementedError
