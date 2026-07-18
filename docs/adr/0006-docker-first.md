# ADR 0006: Docker-first packaging

Date: 2026-07-18
Status: Accepted

## Context

The app should run identically on the owner's machine and any future free
hosting tier, and self-serve a small family and friends user group later.

## Decision

Ship a `python:3.12-slim` image running gunicorn with the app factory, as a
non-root user, with the SQLite cache on a mounted `/data` volume.
`docker-compose.yml` wires the env file (optional), the volume, and a
`/healthz` healthcheck. `.env.example` documents the full configuration
contract; all provider keys are optional.

## Consequences

- `docker compose up` is the only setup step needed to demo the product.
- SQLite on a volume keeps state across container restarts and keeps the
  zero-budget promise; a client-server database is deliberately out of scope.
