from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.append(str(ROOT))

core_spec = importlib.util.spec_from_file_location(
    "crypto_ensemble.core.validators",
    ROOT / "crypto_ensemble" / "core" / "validators.py",
)
validators_module = importlib.util.module_from_spec(core_spec)
sys.modules[core_spec.name] = validators_module
core_spec.loader.exec_module(validators_module)  # type: ignore[union-attr]
validate_trade_v1 = validators_module.validate_trade_v1

norm_spec = importlib.util.spec_from_file_location(
    "normalizer_trade",
    pathlib.Path(__file__).resolve().parents[2] / "normalizer_trade.py",
)
module = importlib.util.module_from_spec(norm_spec)
sys.modules[norm_spec.name] = module
norm_spec.loader.exec_module(module)  # type: ignore[union-attr]
normalize = module.normalize


def test_trade_normalizer_contract():
    frame = {
        "schema": "RawFrame.v2",
        "venue": "binanceus",
        "channel": "trades",
        "stream": "btcusdt@aggTrade",
        "payload": {"s": "BTCUSDT", "p": "1", "q": "2", "m": True, "a": "1"},
        "venue_ts": 0,
        "recv_ts": 0,
        "seq": None,
        "checksum": None,
        "staleness_ms": 0,
        "connection_id": "1",
        "trace_id": "t",
        "size_bytes": 1,
        "codec": "none",
    }
    trade = normalize(frame)
    validate_trade_v1(trade)
    expected = {
        "ts": "1970-01-01T00:00:00+00:00",
        "asset": "BTC-USD",
        "venue": "binanceus",
        "px": 1.0,
        "qty": 2.0,
        "side": "sell",
        "agg_id": "1",
    }
    assert trade == expected
