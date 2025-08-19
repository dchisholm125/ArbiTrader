"""Schema validators using fastjsonschema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import fastjsonschema

ROOT = Path(__file__).resolve().parent / "schemas"


def _compile(schema_name: str) -> Callable[[Any], Any]:
    with open(ROOT / schema_name, "r", encoding="utf-8") as f:
        schema = json.load(f)
    return fastjsonschema.compile(schema)


validate_rawframe_v2 = _compile("RawFrame.v2.json")
validate_orderbook_v1 = _compile("Orderbook.v1.json")
validate_trade_v1 = _compile("Trade.v1.json")
validate_tick_v1 = _compile("Tick.v1.json")
validate_venuestatus_v1 = _compile("VenueStatus.v1.json")

__all__ = [
    "validate_rawframe_v2",
    "validate_orderbook_v1",
    "validate_trade_v1",
    "validate_tick_v1",
    "validate_venuestatus_v1",
]
