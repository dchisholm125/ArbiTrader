from __future__ import annotations

import asyncio
import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.append(str(ROOT))

spec = importlib.util.spec_from_file_location(
    "sink_cold_parquet",
    pathlib.Path(__file__).resolve().parents[2] / "sink_cold_parquet.py",
)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)  # type: ignore[union-attr]
ParquetSink = module.ParquetSink
CEMError = module.CEMError


def test_parquet_sink_jsonl(tmp_path):
    sink = ParquetSink(tmp_path)
    path = asyncio.run(sink.write_batch("t", [{"a": 1}, {"b": 2}]))
    lines = path.read_text().splitlines()
    assert len(lines) == 2
    assert lines[0] == '{"a": 1}'
    assert lines[1] == '{"b": 2}'


def test_parquet_sink_empty_record(tmp_path):
    sink = ParquetSink(tmp_path)
    with pytest.raises(CEMError):
        asyncio.run(sink.write_batch("t", [{}]))
