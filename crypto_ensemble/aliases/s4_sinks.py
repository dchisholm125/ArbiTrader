"""Typed wrappers for sink modules."""

from importlib import import_module

_hot = import_module("crypto_ensemble.1_data.1_ingestion.4_sinks.sink_hot_redis")
_cold = import_module("crypto_ensemble.1_data.1_ingestion.4_sinks.sink_cold_parquet")

RedisPublisher = _hot.RedisPublisher
InMemoryPublisher = _hot.InMemoryPublisher
ParquetSink = _cold.ParquetSink

__all__ = ["RedisPublisher", "InMemoryPublisher", "ParquetSink"]
