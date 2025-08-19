"""Trade normalizer."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from crypto_ensemble.core.errors import SCHEMA_INVALID, UPSTREAM_STALE, CEMError
from crypto_ensemble.core.validators import validate_trade_v1

MAP = yaml.safe_load((Path(__file__).resolve().parent / "symbol_map.yaml").read_text())


def normalize(
    frame: dict[str, Any], staleness_threshold_ms: int = 1000
) -> dict[str, Any]:
    """Normalize a trade RawFrame into Trade.v1."""
    if frame["staleness_ms"] > staleness_threshold_ms:
        raise CEMError(UPSTREAM_STALE, "frame stale")
    payload = frame["payload"]
    sym = payload.get("s")
    asset = MAP.get(sym)
    trade = {
        "ts": datetime.fromtimestamp(
            frame["venue_ts"] / 1000, tz=timezone.utc
        ).isoformat(),
        "asset": asset,
        "venue": frame["venue"],
        "px": float(payload["p"]),
        "qty": float(payload["q"]),
        "side": "sell" if payload.get("m") else "buy",
        "agg_id": payload.get("a"),
    }
    try:
        validate_trade_v1(trade)
    except Exception as exc:  # pragma: no cover - fastjsonschema detail
        raise CEMError(SCHEMA_INVALID, str(exc)) from exc
    return trade
