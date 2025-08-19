"""Logging helpers with structured JSON output."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_json(logger: logging.Logger, **fields: Any) -> None:
    logger.info(json.dumps(fields, default=str))


class Breadcrumbs:
    """Simple breadcrumb trail for debugging."""

    def __init__(self) -> None:
        self._crumbs: list[dict[str, Any]] = []

    def add(self, **fields: Any) -> None:
        fields["ts"] = datetime.utcnow().isoformat()
        self._crumbs.append(fields)

    def trail(self) -> list[dict[str, Any]]:
        return list(self._crumbs)
