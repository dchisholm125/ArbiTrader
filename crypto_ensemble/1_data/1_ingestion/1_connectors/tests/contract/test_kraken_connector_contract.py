from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.append(str(ROOT))
BASE = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(BASE))

spec = importlib.util.spec_from_file_location(
    "kraken_connector", BASE / "kraken_connector.py"
)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)  # type: ignore[union-attr]
KrakenConnector = module.KrakenConnector

publisher_spec = importlib.util.spec_from_file_location(
    "publisher", BASE / "publisher.py"
)
publisher_module = importlib.util.module_from_spec(publisher_spec)
sys.modules[publisher_spec.name] = publisher_module
publisher_spec.loader.exec_module(publisher_module)  # type: ignore[union-attr]
StdoutPublisher = publisher_module.StdoutPublisher

core_spec = importlib.util.spec_from_file_location(
    "crypto_ensemble.core.validators",
    ROOT / "crypto_ensemble" / "core" / "validators.py",
)
core_module = importlib.util.module_from_spec(core_spec)
sys.modules[core_spec.name] = core_module
core_spec.loader.exec_module(core_module)  # type: ignore[union-attr]
validate_rawframe_v2 = core_module.validate_rawframe_v2

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"


def _load(name: str) -> Any:
    with open(FIXTURES / f"{name}.json") as fh:
        return json.load(fh)


def test_kraken_book_snapshot(monkeypatch):
    msg = _load("kraken_book_snapshot")
    expected = _load("kraken_book_snapshot_expected")
    conn = KrakenConnector(StdoutPublisher(), {})
    conn._connection_id = "test-conn"
    monkeypatch.setattr(conn, "_trace_id", lambda *_: "test-trace")
    monkeypatch.setattr(conn, "_size_bytes", lambda _: expected["size_bytes"])
    monkeypatch.setattr(time, "time", lambda: expected["recv_ts"])
    frame = conn.parse_message(msg)
    validate_rawframe_v2(frame)
    assert frame == expected


def test_kraken_book_update(monkeypatch):
    msg = _load("kraken_book_update")
    expected = _load("kraken_book_update_expected")
    conn = KrakenConnector(StdoutPublisher(), {})
    conn._connection_id = "test-conn"
    monkeypatch.setattr(conn, "_trace_id", lambda *_: "test-trace")
    monkeypatch.setattr(conn, "_size_bytes", lambda _: expected["size_bytes"])
    monkeypatch.setattr(time, "time", lambda: expected["recv_ts"])
    frame = conn.parse_message(msg)
    validate_rawframe_v2(frame)
    assert frame == expected


def test_kraken_trade(monkeypatch):
    msg = _load("kraken_trade")
    expected = _load("kraken_trade_expected")
    conn = KrakenConnector(StdoutPublisher(), {})
    conn._connection_id = "test-conn"
    monkeypatch.setattr(conn, "_trace_id", lambda *_: "test-trace")
    monkeypatch.setattr(conn, "_size_bytes", lambda _: expected["size_bytes"])
    monkeypatch.setattr(time, "time", lambda: expected["recv_ts"])
    frame = conn.parse_message(msg)
    validate_rawframe_v2(frame)
    assert frame == expected
