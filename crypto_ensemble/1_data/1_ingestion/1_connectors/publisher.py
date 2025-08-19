"""Publishers for distributing raw frames."""

from __future__ import annotations

from typing import Any

import redis.asyncio as redis


class Publisher:
    async def send(self, topic: str, data: bytes) -> None:
        raise NotImplementedError


class RedisPublisher(Publisher):
    def __init__(self, client: redis.Redis) -> None:
        self.client = client

    async def send(self, topic: str, data: bytes) -> None:
        await self.client.xadd(topic, {"d": data})


class StdoutPublisher(Publisher):
    async def send(self, topic: str, data: bytes) -> None:
        print(topic, data.decode())
