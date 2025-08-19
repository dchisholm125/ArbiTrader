"""In-memory metrics facade."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

CounterKey = Tuple[str, Tuple[Tuple[str, str], ...]]
HistogramKey = CounterKey

_counters: Dict[CounterKey, int] = defaultdict(int)
_hists: Dict[HistogramKey, List[float]] = defaultdict(list)
MAX_LABELS = 10_000


class Counter:
    """Counter metric."""

    def __init__(self, key: CounterKey) -> None:
        self.key = key

    def inc(self, n: int = 1) -> None:
        """Increment counter by ``n``."""
        _counters[self.key] += n


class Histogram:
    """Histogram metric."""

    def __init__(self, key: HistogramKey) -> None:
        self.key = key

    def observe(self, value: float) -> None:
        """Record a value."""
        _hists[self.key].append(value)


def _key(name: str, labels: Dict[str, str]) -> Tuple[str, Tuple[Tuple[str, str], ...]]:
    return name, tuple(sorted(labels.items()))


def counter(name: str, **labels: str) -> Counter:
    """Get a counter metric."""
    key = _key(name, labels)
    if key not in _counters and sum(1 for k in _counters if k[0] == name) >= MAX_LABELS:
        raise ValueError("label cardinality exceeded")
    return Counter(key)


def histogram(name: str, **labels: str) -> Histogram:
    """Get a histogram metric."""
    key = _key(name, labels)
    if key not in _hists and sum(1 for k in _hists if k[0] == name) >= MAX_LABELS:
        raise ValueError("label cardinality exceeded")
    return Histogram(key)


def export() -> Dict[str, Dict[str, object]]:
    """Export current metric snapshot."""
    return {
        "counters": {str(k): v for k, v in _counters.items()},
        "histograms": {str(k): list(v) for k, v in _hists.items()},
    }


def reset() -> None:
    """Clear all metric registries."""
    _counters.clear()
    _hists.clear()
