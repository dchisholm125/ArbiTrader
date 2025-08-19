"""Typed wrappers for health modules."""

from importlib import import_module

_hb = import_module("crypto_ensemble.1_data.1_ingestion.5_health.heartbeat")
_lp = import_module("crypto_ensemble.1_data.1_ingestion.5_health.latency_probe")

Heartbeat = _hb.Heartbeat
LatencyProbe = _lp.LatencyProbe

__all__ = ["Heartbeat", "LatencyProbe"]
