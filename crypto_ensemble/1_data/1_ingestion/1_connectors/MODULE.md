# Connectors

## Purpose
Ingest raw venue data and publish `RawFrame.v2` messages.

## Inputs
WebSocket feeds from venues.

## Outputs
`RawFrame.v2` onto `raw.{venue}.{channel}.{stream}`.

## SLOs
- Publish p99 ≤ 50ms from `venue_ts`.
- Heartbeat every 5s.

## Failure Modes
`IO_TIMEOUT`, `UPSTREAM_STALE`, `RATE_LIMIT`, `SCHEMA_INVALID`, `STATE_CORRUPT`, `DEPENDENCY_UNHEALTHY`.

## Observability
Structured logs and basic metrics.

## Runbook
Start connector with desired publisher. Ensure network connectivity. Heartbeats indicate liveness.

## Acceptance
- Unit tests
- Contract tests validating `RawFrame.v2`
- Linting and type checks
