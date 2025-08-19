"""Cold sink writing Parquet or JSONL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from crypto_ensemble.core.errors import DEPENDENCY_UNHEALTHY, SCHEMA_INVALID, CEMError

try:
    import pyarrow as pa  # type: ignore
    import pyarrow.parquet as pq  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pa = None  # type: ignore
    pq = None  # type: ignore


class ParquetSink:
    """Write records to Parquet; fallback to JSONL if unavailable."""

    def __init__(self, base_dir: str) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def write_batch(self, topic: str, records: Iterable[dict]) -> Path:
        """Write ``records`` to a file and return the path."""
        data: List[dict] = list(records)
        for rec in data:
            if not rec:
                raise CEMError(SCHEMA_INVALID, "empty record")
        path = self.base_dir / f"{topic}.parquet"
        if pa is None or pq is None:
            path = self.base_dir / f"{topic}.jsonl"
            with path.open("w", encoding="utf-8") as f:
                for rec in data:
                    f.write(json.dumps(rec) + "\n")
            return path
        try:  # pragma: no cover - requires pyarrow
            table = pa.Table.from_pylist(data)
            pq.write_table(table, path)
            return path
        except Exception as exc:  # pragma: no cover
            raise CEMError(DEPENDENCY_UNHEALTHY, str(exc)) from exc
