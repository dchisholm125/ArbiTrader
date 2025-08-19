from __future__ import annotations

import asyncio
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.append(str(ROOT))

spec = importlib.util.spec_from_file_location(
    "latency_probe",
    pathlib.Path(__file__).resolve().parents[2] / "latency_probe.py",
)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)  # type: ignore[union-attr]
LatencyProbe = module.LatencyProbe


def test_latency_probe():
    async def fake_rpc() -> None:
        await asyncio.sleep(0)

    times = [0.0, 0.1]
    probe = LatencyProbe(clock=lambda: times.pop(0))
    result = asyncio.run(probe.measure("v", fake_rpc))
    assert result == {"venue": "v", "rtt_ms": 100.0}
