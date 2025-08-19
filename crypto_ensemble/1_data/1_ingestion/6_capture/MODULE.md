# Capture CLI

## Purpose
Capture messages from a subscriber to JSONL.

## Inputs
Topic name, subscriber, count

## Outputs
JSONL file of messages

## SLOs
Write throughput ≥ 100 msg/s

## Failure Modes
`IO_TIMEOUT`, `DEPENDENCY_UNHEALTHY`

## Observability
Counters for captured messages

## Runbook
Invoke CLI with topic, output path, and count.

## Acceptance
Contract tests
