from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.append(str(ROOT))

core_spec = importlib.util.spec_from_file_location(
    "crypto_ensemble.core.errors", ROOT / "crypto_ensemble" / "core" / "errors.py"
)
errors_module = importlib.util.module_from_spec(core_spec)
sys.modules[core_spec.name] = errors_module
core_spec.loader.exec_module(errors_module)  # type: ignore[union-attr]
CEMError = errors_module.CEMError
STATE_CORRUPT = errors_module.STATE_CORRUPT
UPSTREAM_STALE = errors_module.UPSTREAM_STALE

norm_spec = importlib.util.spec_from_file_location(
    "normalizer_orderbook",
    pathlib.Path(__file__).resolve().parents[2] / "normalizer_orderbook.py",
)
module = importlib.util.module_from_spec(norm_spec)
sys.modules[norm_spec.name] = module
norm_spec.loader.exec_module(module)  # type: ignore[union-attr]
normalize = module.normalize


def test_seq_monotonicity():
    frame = {
        "staleness_ms": 0,
        "payload": {"s": "BTCUSDT", "u": 1, "b": [], "a": []},
        "venue_ts": 0,
        "venue": "binanceus",
    }
    normalize(frame)
    frame2 = {
        "staleness_ms": 0,
        "payload": {"s": "BTCUSDT", "u": 1, "b": [], "a": []},
        "venue_ts": 0,
        "venue": "binanceus",
    }
    try:
        normalize(frame2)
    except CEMError as e:
        assert e.code == STATE_CORRUPT
    else:  # pragma: no cover
        assert False


def test_staleness():
    frame = {
        "staleness_ms": 2000,
        "payload": {"s": "BTCUSDT", "u": 2, "b": [], "a": []},
        "venue_ts": 0,
        "venue": "binanceus",
    }
    try:
        normalize(frame, staleness_threshold_ms=1000)
    except CEMError as e:
        assert e.code == UPSTREAM_STALE
    else:  # pragma: no cover
        assert False
