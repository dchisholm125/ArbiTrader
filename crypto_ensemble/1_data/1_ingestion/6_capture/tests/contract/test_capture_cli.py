from __future__ import annotations

import asyncio
import importlib.util
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.append(str(ROOT))

spec = importlib.util.spec_from_file_location(
    "capture_cli",
    pathlib.Path(__file__).resolve().parents[2] / "capture_cli.py",
)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)  # type: ignore[union-attr]
InMemorySubscriber = module.InMemorySubscriber
capture = module.capture
main = module.main
SCHEMA_INVALID = module.SCHEMA_INVALID


def test_capture(tmp_path):
    sub = InMemorySubscriber([b"{}", b"{}"])
    out = tmp_path / "out.jsonl"
    asyncio.run(capture(sub, "t", out, 2, schema=None))
    assert out.read_text().splitlines() == ["{}", "{}"]


def test_capture_schema_failure(tmp_path, monkeypatch, capsys):
    out = tmp_path / "out.jsonl"
    sub = InMemorySubscriber([b"{}"])
    monkeypatch.setattr(module, "InMemorySubscriber", lambda queue=None: sub)

    def failing(_: dict) -> None:
        raise ValueError("bad")

    monkeypatch.setitem(module.VALIDATORS, "RawFrame.v2", failing)
    args = ["--topic", "t", "--out", str(out), "--n", "1", "--schema", "RawFrame.v2"]
    with pytest.raises(SystemExit):
        main(args)
    err = capsys.readouterr().err.strip()
    j = json.loads(err)
    assert j["code"] == SCHEMA_INVALID
