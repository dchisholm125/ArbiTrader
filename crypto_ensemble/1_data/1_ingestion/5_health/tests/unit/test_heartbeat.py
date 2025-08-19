from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.append(str(ROOT))

spec = importlib.util.spec_from_file_location(
    "heartbeat",
    pathlib.Path(__file__).resolve().parents[2] / "heartbeat.py",
)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)  # type: ignore[union-attr]
Heartbeat = module.Heartbeat


def test_heartbeat_shape():
    items: list[dict] = []
    hb = Heartbeat(items.append, latency_ms_p95=1.2)
    hb.set_reconnects_total(3)
    payload = hb.tick("m", "1")
    assert items[0] == payload
    assert payload["latency_ms_p95"] == 1.2
    assert payload["reconnects_total"] == 3
