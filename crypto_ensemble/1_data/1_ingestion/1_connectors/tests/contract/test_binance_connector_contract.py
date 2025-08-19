from __future__ import annotations

import importlib.util
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.append(str(ROOT))

BASE = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(BASE))
spec = importlib.util.spec_from_file_location(
    "binance_us_connector", BASE / "binance_us_connector.py"
)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)  # type: ignore[union-attr]
BinanceUSConnector = module.BinanceUSConnector

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


def test_orderbook_frame(monkeypatch):
    cfg = {
        "symbols": ["BTCUSDT"],
        "orderbook": {"enabled": True},
        "trades": {"enabled": False},
    }
    conn = BinanceUSConnector(StdoutPublisher(), cfg)
    msg = {
        "stream": "btcusdt@depth",
        "data": {"E": 1000, "s": "BTCUSDT", "b": [["1", "2"]], "a": [["3", "4"]]},
    }
    monkeypatch.setattr(time, "time", lambda: 2.0)
    frame = conn.parse_message(msg)
    validate_rawframe_v2(frame)
    expected = {
        "schema": "RawFrame.v2",
        "venue": "binanceus",
        "channel": "orderbook",
        "stream": "btcusdt@depth",
        "payload": msg["data"],
        "venue_ts": 1000,
        "recv_ts": 2000.0,
        "seq": None,
        "checksum": None,
        "staleness_ms": 1000,
        "connection_id": "conn-1",
        "trace_id": "2000",
        "size_bytes": len(str(msg["data"]).encode()),
        "codec": "none",
    }
    assert frame == expected


def test_trade_frame(monkeypatch):
    cfg = {
        "symbols": ["BTCUSDT"],
        "orderbook": {"enabled": False},
        "trades": {"enabled": True},
    }
    conn = BinanceUSConnector(StdoutPublisher(), cfg)
    msg = {
        "stream": "btcusdt@aggTrade",
        "data": {"E": 1500, "s": "BTCUSDT", "p": "10", "q": "1", "m": True},
    }
    monkeypatch.setattr(time, "time", lambda: 3.0)
    frame = conn.parse_message(msg)
    validate_rawframe_v2(frame)
    expected = {
        "schema": "RawFrame.v2",
        "venue": "binanceus",
        "channel": "trades",
        "stream": "btcusdt@aggTrade",
        "payload": msg["data"],
        "venue_ts": 1500,
        "recv_ts": 3000.0,
        "seq": None,
        "checksum": None,
        "staleness_ms": 1500,
        "connection_id": "conn-1",
        "trace_id": "3000",
        "size_bytes": len(str(msg["data"]).encode()),
        "codec": "none",
    }
    assert frame == expected
