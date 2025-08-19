# Health Utilities

## Purpose
Emit heartbeats and measure RPC latency.

## Inputs
Module identifiers, RPC callables

## Outputs
Heartbeat dicts, latency measurements

## SLOs
Heartbeat tick < 1ms, probe accuracy ±1ms

## Failure Modes
`DEPENDENCY_UNHEALTHY`

## Observability
Structured logs

## Runbook
Invoke heartbeat.tick periodically; use latency probe against dependencies.

## Acceptance
Unit tests
