"""Typed wrapper for router module."""

from importlib import import_module

router_mod = import_module("crypto_ensemble.1_data.1_ingestion.3_router.router")
Router = router_mod.Router
__all__ = ["Router"]
