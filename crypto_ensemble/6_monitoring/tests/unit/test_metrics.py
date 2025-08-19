from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

BASE = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(BASE))

spec = importlib.util.spec_from_file_location(
    "metrics",
    BASE / "metrics.py",
)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)  # type: ignore[union-attr]
counter = module.counter
histogram = module.histogram
export = module.export
reset = module.reset


def test_counter_and_histogram():
    reset()
    c = counter("x", a="1")
    c.inc()
    c.inc(2)
    h = histogram("y")
    h.observe(1.0)
    snap = export()
    assert "('x', (('a', '1'),))" in snap["counters"]
    assert snap["counters"]["('x', (('a', '1'),))"] == 3
    assert "('y', ())" in snap["histograms"]
    assert snap["histograms"]["('y', ())"] == [1.0]
    reset()
    assert export() == {"counters": {}, "histograms": {}}


def test_cardinality_guard():
    reset()
    for i in range(10_000):
        counter("c", lab=str(i)).inc()
    with pytest.raises(ValueError):
        counter("c", lab="overflow").inc()
