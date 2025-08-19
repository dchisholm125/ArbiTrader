"""Typed wrappers for capture module."""

from importlib import import_module

_cap = import_module("crypto_ensemble.1_data.1_ingestion.6_capture.capture_cli")

InMemorySubscriber = _cap.InMemorySubscriber
Subscriber = _cap.Subscriber
capture = _cap.capture
main = _cap.main

__all__ = ["InMemorySubscriber", "Subscriber", "capture", "main"]
