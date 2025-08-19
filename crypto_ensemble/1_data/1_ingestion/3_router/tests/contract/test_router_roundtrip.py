from __future__ import annotations

import importlib.util
import pathlib
import sys
import zlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.append(str(ROOT))

BASE = pathlib.Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location("router", BASE / "router.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)  # type: ignore[union-attr]
Router = module.Router


class DummyPublisher:
    def __init__(self) -> None:
        self.sent: list[bytes] = []

    async def send(self, topic: str, data: bytes) -> None:
        self.sent.append(data)


import asyncio


def test_router_compress():
    pub = DummyPublisher()
    router = Router(pub)
    asyncio.run(router.publish("t", {"a": 1}))
    assert len(pub.sent) == 1
    assert zlib.decompress(pub.sent[0]) == b'{"a": 1}'


def test_router_no_compress():
    pub = DummyPublisher()
    router = Router(pub)
    asyncio.run(router.publish("t", {"a": 1}, compress=False))
    assert pub.sent[0] == b'{"a": 1}'


def test_router_error(monkeypatch):
    class BadPub:
        async def send(self, topic: str, data: bytes) -> None:
            raise RuntimeError("boom")

    errors: list[dict] = []
    router = Router(BadPub(), on_error=errors.append)
    with pytest.raises(module.CEMError):
        asyncio.run(router.publish("t", {"a": 1}))
    assert errors and errors[0]["code"] == module.DEPENDENCY_UNHEALTHY
