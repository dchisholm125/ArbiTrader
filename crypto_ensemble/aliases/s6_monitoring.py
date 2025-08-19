"""Typed wrappers for monitoring metrics."""

from importlib import import_module

_metrics = import_module("crypto_ensemble.6_monitoring.metrics")
counter = _metrics.counter
histogram = _metrics.histogram
reset = _metrics.reset
__all__ = ["counter", "histogram", "reset"]
