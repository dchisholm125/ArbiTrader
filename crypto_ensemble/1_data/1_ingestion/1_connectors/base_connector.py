"""Base connector utilities."""

from __future__ import annotations

import asyncio
import json
import random
import time
from dataclasses import dataclass
from typing import Any, Optional

from crypto_ensemble.core.errors import IO_TIMEOUT, CEMError
from crypto_ensemble.core.validators import validate_rawframe_v2


@dataclass
class BackoffPolicy:
    backoff_ms_min: int = 250
    backoff_ms_max: int = 3000
    jitter: float = 0.1

    def next_delay(self, attempt: int) -> float:
        base = min(self.backoff_ms_max, self.backoff_ms_min * (2**attempt))
        jitter = random.uniform(-self.jitter, self.jitter) * base
        return (base + jitter) / 1000


class BaseConnector:
    venue: str

    def __init__(self, publisher: Any, backoff: BackoffPolicy | None = None) -> None:
        self.publisher = publisher
        self.backoff = backoff or BackoffPolicy()
        self._connection_id = "conn-1"

    async def heartbeat(self) -> None:
        while True:
            await asyncio.sleep(5)

    def _raw_frame(
        self,
        *,
        channel: str,
        stream: str,
        payload: dict[str, Any],
        venue_ts: float,
        seq: Optional[int] = None,
        checksum: Optional[str] = None,
    ) -> dict[str, Any]:
        recv_ts = time.time() * 1000
        data = {
            "schema": "RawFrame.v2",
            "venue": self.venue,
            "channel": channel,
            "stream": stream,
            "payload": payload,
            "venue_ts": venue_ts,
            "recv_ts": recv_ts,
            "seq": seq,
            "checksum": checksum,
            "staleness_ms": int(recv_ts - venue_ts),
            "connection_id": self._connection_id,
            "trace_id": f"{int(recv_ts)}",
            "size_bytes": len(str(payload).encode()),
            "codec": "none",
        }
        validate_rawframe_v2(data)
        return data

    async def publish_raw(self, topic: str, data: dict[str, Any]) -> None:
        await self.publisher.send(topic, json.dumps(data).encode())

    async def run(self) -> None:  # pragma: no cover - to be implemented by subclasses
        raise NotImplementedError
