from __future__ import annotations

import importlib.util
import pathlib
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.append(str(ROOT))

core_spec = importlib.util.spec_from_file_location(
    "crypto_ensemble.core.validators",
    ROOT / "crypto_ensemble" / "core" / "validators.py",
)
validators_module = importlib.util.module_from_spec(core_spec)
sys.modules[core_spec.name] = validators_module
core_spec.loader.exec_module(validators_module)  # type: ignore[union-attr]
validate_tick_v1 = validators_module.validate_tick_v1

composer_spec = importlib.util.spec_from_file_location(
    "tick_composer",
    pathlib.Path(__file__).resolve().parents[2] / "tick_composer.py",
)
composer_module = importlib.util.module_from_spec(composer_spec)
sys.modules[composer_spec.name] = composer_module
composer_spec.loader.exec_module(composer_module)  # type: ignore[union-attr]
TickComposer = composer_module.TickComposer
CEMError = importlib.import_module("crypto_ensemble.core.errors").CEMError
UPSTREAM_STALE = importlib.import_module("crypto_ensemble.core.errors").UPSTREAM_STALE


def sample_ob() -> dict[str, object]:
    return {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "asset": "btc_usd",
        "venue": "binanceus",
        "seq": 1,
        "checksum": "x",
        "l2": [
            {"px": 1.0, "qty": 1.0, "side": "bid"},
            {"px": 2.0, "qty": 1.0, "side": "ask"},
        ],
        "spread_bps": None,
    }


def sample_trade() -> dict[str, object]:
    return {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "asset": "btc_usd",
        "venue": "binanceus",
        "px": 1.5,
        "qty": 2.0,
        "side": "buy",
        "agg_id": None,
    }


def test_tick_output():
    comp = TickComposer(staleness_ms=10**9)
    comp.update_orderbook(sample_ob())
    comp.update_trade(sample_trade())
    tick = comp.maybe_emit_tick("btc_usd", "binanceus")
    assert tick is not None
    validate_tick_v1(tick)


def test_tick_staleness():
    comp = TickComposer(staleness_ms=0)
    ob = sample_ob()
    tr = sample_trade()
    ob["ts"] = "1970-01-01T00:00:00+00:00"
    tr["ts"] = "1970-01-01T00:00:00+00:00"
    comp.update_orderbook(ob)
    comp.update_trade(tr)
    try:
        comp.maybe_emit_tick("btc_usd", "binanceus")
    except CEMError as e:
        assert e.code == UPSTREAM_STALE
    else:  # pragma: no cover
        assert False


def test_tick_latency():
    comp = TickComposer(staleness_ms=10**9)
    ob = sample_ob()
    tr = sample_trade()
    comp.update_orderbook(ob)
    comp.update_trade(tr)
    start = time.perf_counter()
    for _ in range(1000):
        comp.maybe_emit_tick("btc_usd", "binanceus")
    duration_ms = (time.perf_counter() - start) * 1000
    assert duration_ms < 20.0
