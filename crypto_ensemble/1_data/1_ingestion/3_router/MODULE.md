# Router

## Purpose
Compress and route normalized messages to publishers.

## Inputs
Canonical dicts

## Outputs
Bytes to publisher

## SLOs
Compression overhead < 5ms

## Failure Modes
`IO_TIMEOUT`, `DEPENDENCY_UNHEALTHY`

## Observability
Metrics around publish latency

## Runbook
Ensure publisher connectivity

## Acceptance
Contract tests
