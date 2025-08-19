"""Orderbook normalizer."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from crypto_ensemble.core.errors import STATE_CORRUPT, UPSTREAM_STALE, CEMError
from crypto_ensemble.core.validators import validate_orderbook_v1

MAP = yaml.safe_load((Path(__file__).resolve().parent / "symbol_map.yaml").read_text())
_last_seq: dict[str, int] = {}


def normalize(
    frame: dict[str, Any], staleness_threshold_ms: int = 1000
) -> dict[str, Any]:
    if frame["staleness_ms"] > staleness_threshold_ms:
        raise CEMError(UPSTREAM_STALE, "frame stale")
    payload = frame["payload"]
    sym = payload.get("s")
    asset = MAP.get(sym)
    seq = payload.get("u", 0)
    last = _last_seq.get(sym)
    if last is not None and seq <= last:
        raise CEMError(STATE_CORRUPT, "non-monotonic seq")
    _last_seq[sym] = seq
    checksum = hashlib.md5(str(seq).encode()).hexdigest()
    ob = {
        "ts": datetime.fromtimestamp(
            frame["venue_ts"] / 1000, tz=timezone.utc
        ).isoformat(),
        "asset": asset,
        "venue": frame["venue"],
        "seq": seq,
        "checksum": checksum,
        "l2": [
            {"px": float(b[0]), "qty": float(b[1]), "side": "bid"}
            for b in payload.get("b", [])
        ]
        + [
            {"px": float(a[0]), "qty": float(a[1]), "side": "ask"}
            for a in payload.get("a", [])
        ],
        "spread_bps": None,
    }
    validate_orderbook_v1(ob)
    return ob
