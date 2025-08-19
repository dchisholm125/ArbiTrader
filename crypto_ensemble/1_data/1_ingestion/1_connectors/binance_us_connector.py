"""Binance.US WebSocket connector."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict

from base_connector import BaseConnector

import websockets
from crypto_ensemble.core.errors import IO_TIMEOUT, SCHEMA_INVALID, CEMError
from crypto_ensemble.core.validators import validate_rawframe_v2

STREAM_MAP = {
    "depth": "orderbook",
    "aggtrade": "trades",
}


class BinanceUSConnector(BaseConnector):
    venue = "binanceus"

    def __init__(self, publisher: Any, config: Dict[str, Any]) -> None:
        super().__init__(publisher)
        self.config = config

    def parse_message(self, msg: dict[str, Any]) -> dict[str, Any]:
        stream = msg["stream"]
        payload = msg["data"]
        suffix = stream.split("@")[-1]
        channel = STREAM_MAP.get(suffix.lower())
        if not channel:
            raise CEMError(SCHEMA_INVALID, f"unknown stream {stream}")
        venue_ts = payload.get("E", int(time.time() * 1000))
        frame = self._raw_frame(
            channel=channel, stream=stream, payload=payload, venue_ts=venue_ts
        )
        validate_rawframe_v2(frame)
        return frame

    async def _connect(self) -> websockets.WebSocketClientProtocol:
        symbols = [s.lower() for s in self.config["symbols"]]
        streams = []
        if self.config.get("orderbook", {}).get("enabled"):
            streams.extend(f"{s}@depth" for s in symbols)
        if self.config.get("trades", {}).get("enabled"):
            channel = self.config["trades"].get("channel", "aggTrade").lower()
            streams.extend(f"{s}@{channel}" for s in symbols)
        url = "wss://stream.binance.us:9443/stream?streams=" + "/".join(streams)
        return await websockets.connect(url, ping_interval=None)

    async def run(self) -> None:
        attempt = 0
        while True:
            try:
                ws = await self._connect()
                attempt = 0
                async for msg in ws:
                    data = json.loads(msg)
                    frame = self.parse_message(data)
                    topic = f"raw.{self.venue}.{frame['channel']}.{frame['stream']}"
                    await self.publish_raw(topic, frame)
            except asyncio.TimeoutError as e:
                raise CEMError(IO_TIMEOUT, "idle timeout") from e
            except CEMError:
                raise
            except Exception as e:  # pragma: no cover - network errors
                delay = self.backoff.next_delay(attempt)
                attempt += 1
                await asyncio.sleep(delay)
            finally:
                try:
                    await ws.close()
                except Exception:
                    pass
