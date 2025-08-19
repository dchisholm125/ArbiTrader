"""CLI to capture messages to JSONL."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Protocol

from crypto_ensemble.core.errors import SCHEMA_INVALID, CEMError
from crypto_ensemble.core.validators import (
    validate_orderbook_v1,
    validate_rawframe_v2,
    validate_tick_v1,
    validate_trade_v1,
)


class Subscriber(Protocol):
    """Simple subscriber interface."""

    async def recv(self, topic: str) -> bytes:
        """Receive a message for topic."""


@dataclass
class InMemorySubscriber:
    """In-memory queue subscriber for tests."""

    queue: List[bytes]

    async def recv(self, topic: str) -> bytes:  # pragma: no cover - trivial
        return self.queue.pop(0)


VALIDATORS: dict[str, Callable[[dict], None]] = {
    "RawFrame.v2": validate_rawframe_v2,
    "Orderbook.v1": validate_orderbook_v1,
    "Trade.v1": validate_trade_v1,
    "Tick.v1": validate_tick_v1,
}


async def capture(
    sub: Subscriber, topic: str, out: Path, n: int, schema: str | None = None
) -> None:
    """Capture ``n`` messages into ``out`` file validating each payload."""
    validator = VALIDATORS.get(schema) if schema else None
    with out.open("w", encoding="utf-8") as f:
        for _ in range(n):
            data = await sub.recv(topic)
            obj = json.loads(data.decode())
            if validator:
                try:
                    validator(obj)
                except Exception as exc:  # pragma: no cover - validator detail
                    raise CEMError(SCHEMA_INVALID, str(exc)) from exc
            f.write(json.dumps(obj) + "\n")


def main(argv: list[str] | None = None) -> None:  # pragma: no cover - CLI wrapper
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument(
        "--schema", choices=list(VALIDATORS.keys()), required=False, default=None
    )
    args = parser.parse_args(argv)
    sub = InMemorySubscriber([])
    try:
        asyncio.run(capture(sub, args.topic, Path(args.out), args.n, args.schema))
    except CEMError as exc:  # pragma: no cover - CLI error path
        sys.stderr.write(json.dumps(exc.to_dict()) + "\n")
        raise SystemExit(1) from exc


if __name__ == "__main__":  # pragma: no cover
    main()
