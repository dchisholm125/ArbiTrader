"""Canonical Error Model implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(slots=True)
class CEMError(Exception):
    code: str
    message: str
    context: Optional[dict[str, Any]] = None
    retryable: bool = True

    def __str__(self) -> str:  # pragma: no cover - simple passthrough
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "context": self.context or {},
            "retryable": self.retryable,
        }


IO_TIMEOUT = "IO_TIMEOUT"
UPSTREAM_STALE = "UPSTREAM_STALE"
RATE_LIMIT = "RATE_LIMIT"
SCHEMA_INVALID = "SCHEMA_INVALID"
STATE_CORRUPT = "STATE_CORRUPT"
DEPENDENCY_UNHEALTHY = "DEPENDENCY_UNHEALTHY"

__all__ = [
    "CEMError",
    "IO_TIMEOUT",
    "UPSTREAM_STALE",
    "RATE_LIMIT",
    "SCHEMA_INVALID",
    "STATE_CORRUPT",
    "DEPENDENCY_UNHEALTHY",
]
