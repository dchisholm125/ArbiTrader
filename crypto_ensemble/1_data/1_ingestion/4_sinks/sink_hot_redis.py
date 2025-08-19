"""Publish messages to Redis streams."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Protocol

from crypto_ensemble.core.errors import DEPENDENCY_UNHEALTHY, CEMError

try:
    import redis.asyncio as redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None  # type: ignore


class Publisher(Protocol):
    """Interface for async byte publishers."""

    async def send(self, topic: str, data: bytes) -> None:
        """Send bytes to a topic."""


class RedisPublisher(Publisher):
    """Publisher backed by Redis XADD."""

    def __init__(self, url: str, stream: str) -> None:
        if redis is None:  # pragma: no cover - depends on external lib
            raise CEMError(DEPENDENCY_UNHEALTHY, "redis.asyncio unavailable")
        self.client = redis.from_url(url)
        self.stream = stream

    async def send(self, topic: str, data: bytes) -> None:
        """Send ``data`` to the configured Redis stream."""
        await self.client.xadd(self.stream or topic, {"d": data})


class InMemoryPublisher(Publisher):
    """In-memory publisher for tests."""

    def __init__(self) -> None:
        self.messages: Dict[str, List[bytes]] = defaultdict(list)

    async def send(self, topic: str, data: bytes) -> None:
        self.messages[topic].append(data)
