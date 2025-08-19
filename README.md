# Crypto Ensemble

Foundation for crypto multi-venue ingestion & normalization.

## Binance.US Connector Demo

```bash
python -m crypto_ensemble.1_data.1_ingestion.1_connectors.binance_us_connector
```
(uses `StdoutPublisher` by default)

## Tests

```bash
make test-unit
make test-contract
make test-chain
make verify-module
```

## Capture Sample Data

```bash
python -m crypto_ensemble.1_data.1_ingestion.6_capture.capture_cli --topic raw.binanceus.orderbook.btcusdt@depth --out out.jsonl --n 10 --schema RawFrame.v2
```

## Run Normalizers on Captured Frames

```python
from crypto_ensemble.1_data.1_ingestion.2_normalizer import normalizer_orderbook
import json
frame = json.loads(open("out.jsonl").readline())
print(normalizer_orderbook.normalize(frame))
```

Redis and pyarrow are optional; in CI we use in-memory stubs and JSONL fallbacks.
Numeric directory names are shimmed for type checking via `crypto_ensemble/aliases` and `crypto_ensemble/stubs`.

## End-to-End Runner

```bash
python -m apps.ingest_normalize_runner --venue binanceus --symbols BTCUSDT,ETHUSDT --stdout
```

See `examples/mini.yml` for a sample configuration.
