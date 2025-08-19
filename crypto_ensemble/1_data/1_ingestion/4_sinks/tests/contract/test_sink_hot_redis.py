from __future__ import annotations

import asyncio
import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.append(str(ROOT))

spec = importlib.util.spec_from_file_location(
    "sink_hot_redis",
    pathlib.Path(__file__).resolve().parents[2] / "sink_hot_redis.py",
)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)  # type: ignore[union-attr]
InMemoryPublisher = module.InMemoryPublisher
RedisPublisher = module.RedisPublisher
DEPENDENCY_UNHEALTHY = module.DEPENDENCY_UNHEALTHY
CEMError = module.CEMError


def test_inmemory_publisher_multi_topic():
    pub = InMemoryPublisher()
    asyncio.run(pub.send("a", b"1"))
    asyncio.run(pub.send("b", b"2"))
    assert pub.messages == {"a": [b"1"], "b": [b"2"]}


def test_redis_missing(monkeypatch):
    monkeypatch.setattr(module, "redis", None)
    with pytest.raises(CEMError) as exc:
        RedisPublisher("redis://", "s")
    assert exc.value.code == DEPENDENCY_UNHEALTHY
