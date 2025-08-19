"""Run chain tests using promoted fixtures."""

from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path
from typing import Optional

BASE = Path(__file__).resolve().parents[2]
ROOT = BASE / "crypto_ensemble"
import sys

sys.path.append(str(BASE))
FIXT_RAW = Path(__file__).resolve().parent / "fixtures" / "promoted" / "raw"
OUT_DIR = Path(__file__).resolve().parent / "fixtures" / "promoted" / "normalized"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# load normalizers
order_spec = importlib.util.spec_from_file_location(
    "normalizer_orderbook",
    ROOT / "1_data/1_ingestion/2_normalizer/normalizer_orderbook.py",
)
order_mod = importlib.util.module_from_spec(order_spec)
order_spec.loader.exec_module(order_mod)  # type: ignore[union-attr]

trade_spec = importlib.util.spec_from_file_location(
    "normalizer_trade",
    ROOT / "1_data/1_ingestion/2_normalizer/normalizer_trade.py",
)
trade_mod = importlib.util.module_from_spec(trade_spec)
trade_spec.loader.exec_module(trade_mod)  # type: ignore[union-attr]

val_spec = importlib.util.spec_from_file_location(
    "validators",
    ROOT / "core" / "validators.py",
)
val_mod = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(val_mod)  # type: ignore[union-attr]
validate_orderbook_v1 = val_mod.validate_orderbook_v1
validate_trade_v1 = val_mod.validate_trade_v1
validate_tick_v1 = val_mod.validate_tick_v1


async def run() -> None:
    summary = {"count": 0, "first_ts": None, "last_ts": None}
    prev_seq: Optional[int] = None
    for file in FIXT_RAW.glob("*.json"):
        frame = json.loads(file.read_text())
        summary["count"] += 1
        summary["first_ts"] = summary["first_ts"] or frame["venue_ts"]
        summary["last_ts"] = frame["venue_ts"]
        if frame["channel"] == "orderbook":
            ob = order_mod.normalize(frame)
            validate_orderbook_v1(ob)
            if prev_seq is not None and ob["seq"] <= prev_seq:
                raise AssertionError("non-monotonic seq")
            prev_seq = ob["seq"]
            (OUT_DIR / "orderbook.json").write_text(json.dumps(ob))
        elif frame["channel"] == "trades":
            tr = trade_mod.normalize(frame)
            validate_trade_v1(tr)
            (OUT_DIR / "trade.json").write_text(json.dumps(tr))
    # compose tick
    tick_spec = importlib.util.spec_from_file_location(
        "tick_composer",
        ROOT / "1_data/1_ingestion/2_normalizer/tick_composer.py",
    )
    tick_mod = importlib.util.module_from_spec(tick_spec)
    tick_spec.loader.exec_module(tick_mod)  # type: ignore[union-attr]
    composer = tick_mod.TickComposer(staleness_ms=1_000_000)
    ob = json.loads((OUT_DIR / "orderbook.json").read_text())
    tr = json.loads((OUT_DIR / "trade.json").read_text())
    composer.update_orderbook(ob)
    composer.update_trade(tr)
    ob_ts = int(
        __import__("datetime").datetime.fromisoformat(ob["ts"]).timestamp() * 1000
    )
    tr_ts = int(
        __import__("datetime").datetime.fromisoformat(tr["ts"]).timestamp() * 1000
    )
    import time as _t

    _t.time = lambda: max(ob_ts, tr_ts) / 1000  # type: ignore
    tick = composer.maybe_emit_tick(ob["asset"], ob["venue"])
    validate_tick_v1(tick)
    (OUT_DIR / "tick.json").write_text(json.dumps(tick))
    print(json.dumps(summary))


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(run())
