#!/usr/bin/env python3
"""Mini runner: connector → RawFrame → normalizers → stdout/redis."""

from __future__ import annotations

import asyncio
import json
import signal
from argparse import ArgumentParser
from typing import Any

from crypto_ensemble.aliases.s1_data import connectors as connectors_pkg
from crypto_ensemble.aliases.s1_data import normalizer as normalizer_pkg
from crypto_ensemble.aliases.s2_core import (
    validate_orderbook_v1,
    validate_trade_v1,
)

StdoutPublisher = connectors_pkg.publisher.StdoutPublisher
BinanceUSConnector = connectors_pkg.binance_us_connector.BinanceUSConnector
CoinbaseConnector = connectors_pkg.coinbase_connector.CoinbaseConnector
KrakenConnector = connectors_pkg.kraken_connector.KrakenConnector
normalize_orderbook = normalizer_pkg.normalizer_orderbook.normalize
normalize_trade = normalizer_pkg.normalizer_trade.normalize


async def main() -> None:
    """Run a connector and normalize its output to stdout."""
    ap = ArgumentParser()
    ap.add_argument(
        "--venue", choices=["binanceus", "coinbase", "kraken"], required=True
    )
    ap.add_argument(
        "--symbols",
        required=True,
        help="comma-separated (e.g. BTCUSDT,ETHUSDT or BTC-USD)",
    )
    ap.add_argument("--stdout", action="store_true", help="mirror normalized to stdout")
    args = ap.parse_args()

    symbols = [s.strip() for s in args.symbols.split(",")]
    publisher = StdoutPublisher()

    if args.venue == "binanceus":
        connector = BinanceUSConnector(
            publisher,
            {
                "symbols": symbols,
                "orderbook": {"enabled": True, "mode": "diff", "interval_ms": 100},
                "trades": {"enabled": True, "channel": "aggTrade"},
            },
        )
    elif args.venue == "coinbase":
        connector = CoinbaseConnector(publisher, {"symbols": symbols})
    else:
        connector = KrakenConnector(publisher, {"symbols": symbols})

    async def on_raw(_topic: str, frame: dict[str, Any]) -> None:
        ch = frame["channel"]
        if ch.startswith("orderbook"):
            ob = normalize_orderbook(frame)
            validate_orderbook_v1(ob)
            if args.stdout:
                print("normalized.orderbook", json.dumps(ob))
        elif ch.startswith("trades"):
            tr = normalize_trade(frame)
            validate_trade_v1(tr)
            if args.stdout:
                print("normalized.trade", json.dumps(tr))

    async def publish_raw(topic: str, data: dict[str, Any]) -> None:
        await on_raw(topic, data)

    connector.publish_raw = publish_raw  # type: ignore[assignment]

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    async def runner() -> None:
        try:
            await connector.run()
        except NotImplementedError:
            print(f"run() not implemented for {args.venue}")

    task = asyncio.create_task(runner())
    await stop.wait()
    task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
