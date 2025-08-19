# Normalizers

## Purpose
Transform raw frames into canonical records.

## Inputs
RawFrame.v2

## Outputs
Orderbook.v1, Trade.v1, Tick.v1

## SLOs
Validation latency < 10ms
Tick composition p99 < 1ms

## Failure Modes
`UPSTREAM_STALE`, `STATE_CORRUPT`, `SCHEMA_INVALID`

## Observability
Structured logs, metrics

## Runbook
Deploy alongside connectors. Ensure symbol map is up to date.

## Acceptance
Unit and contract tests
