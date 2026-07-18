# ADR 0002: Canonical package layout under app/

Date: 2026-07-18
Status: Accepted

## Context

The repo carried two divergent implementations: a Flask path in `app/` using
CarAPI and a library path in `src/vin_lookup/` aggregating NHTSA, MarketCheck,
and CarMD. They shared no code and drifted apart, and the `src/` copy
contained hardcoded credentials.

## Decision

One canonical package: `app/`, organized by responsibility.

- `app/domain/` pure VIN logic with no I/O: check digit, model year, WMI,
  parsing, typo suggestions, and the normalized `VehicleRecord`.
- `app/providers/` one module per data source behind a shared `VinProvider`
  interface plus a registry.
- `app/consensus/` cross-provider agreement and confidence.
- `app/services/` orchestration (lookup, explorer).
- `app/cache/` SQLite persistence.
- `app/routes/` Flask blueprints split into pages, HTMX partials, and JSON API.

`src/` and `utils/` are deleted. `setup.py` is replaced by `pyproject.toml`.

## Consequences

- Domain logic is import-light and unit testable without network or Flask.
- New providers touch only `app/providers/` and the registry list.
