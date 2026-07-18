# ADR 0007: SQLite cache with per-provider TTL

Date: 2026-07-18
Status: Accepted

## Context

Free provider tiers are rate limited and occasionally slow or down. Repeat
lookups of the same VIN are common (sharing a result with family, refreshing
a page). Zero budget rules out managed databases and caches.

## Decision

A single SQLite file (WAL mode, stdlib `sqlite3`, no ORM) with three tables:

- `provider_responses`: raw payload per (vin, provider) with fetch time,
  status, and latency. TTL 30 days. On lookup, only stale or missing
  providers are refetched; fresh raw payloads are re-mapped and consensus is
  recomputed, so mapper and engine improvements apply to cached data
  immediately.
- `vin_lookups`: denormalized summary (make, model, year, confidence) per
  VIN with hit count, powering the recently searched list without joins.
  Carries `schema_version` to invalidate summaries after engine changes.
- `catalog_cache`: makes and models payloads for the explorer, TTL 7 days.

`?refresh=1` bypasses the cache. Connections are short lived per call with
`busy_timeout`, which is safe under two gunicorn workers at this scale.

## Consequences

- Repeat lookups are instant and cost zero provider quota.
- Cached raw payloads mean provider mappers can evolve without refetching.
- SQLite on a Docker volume is the persistence story; scaling beyond a
  small user group would revisit this.
