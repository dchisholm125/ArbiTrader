"""Router to publish messages to a byte publisher."""

from __future__ import annotations

import json
import zlib
from typing import Any, Callable, Dict

from crypto_ensemble.core.errors import (
    DEPENDENCY_UNHEALTHY,
    SCHEMA_INVALID,
    CEMError,
)


class Router:
    """Publish JSON messages via an async byte publisher."""

    def __init__(
        self,
        publisher: Any,
        on_error: Callable[[Dict[str, Any]], None] | None = None,
    ) -> None:
        """Initialize router with a publisher and optional error hook."""
        self.publisher = publisher
        self.on_error = on_error

    async def publish(
        self, topic: str, msg: dict[str, Any], compress: bool = True
    ) -> None:
        """Serialize and publish ``msg`` to ``topic``.

        Raises
        ------
        CEMError
            If inputs are invalid or the publisher fails.
        """
        if not topic or not isinstance(msg, dict):
            raise CEMError(SCHEMA_INVALID, "invalid publish inputs")
        data = json.dumps(msg).encode()
        if compress:
            data = zlib.compress(data)
        try:
            await self.publisher.send(topic, data)
        except Exception as exc:  # pragma: no cover - depends on publisher
            cem = CEMError(DEPENDENCY_UNHEALTHY, str(exc))
            if self.on_error:
                self.on_error(cem.to_dict())
            raise cem
