# Sinks

## Purpose
Persist data to hot Redis streams or cold Parquet/JSONL files.

## Inputs
Bytes or normalized records

## Outputs
Redis stream entries, Parquet/JSONL files

## SLOs
XADD latency < 5ms, file flush < 10ms

## Failure Modes
`DEPENDENCY_UNHEALTHY`, `IO_TIMEOUT`

## Observability
Monitor Redis responses

## Runbook
Ensure Redis reachable

## Acceptance
Contract tests
