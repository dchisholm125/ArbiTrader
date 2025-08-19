"""Entry points for data ingestion modules."""

from importlib import import_module

connectors = import_module("crypto_ensemble.1_data.1_ingestion.1_connectors")
normalizer = import_module("crypto_ensemble.1_data.1_ingestion.2_normalizer")
__all__ = ["connectors", "normalizer"]
