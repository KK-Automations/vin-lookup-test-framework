# ADR 0012: Render as the hosted deployment target

Date: 2026-07-19
Status: Accepted

## Context

The app is self-serve for a small family and friends group in addition to
being a portfolio piece, so it needs a URL beyond localhost. It is already
Docker-first (ADR 0006), so the natural fit is a platform that deploys a
Dockerfile directly rather than one requiring a separate buildpack or
rewritten entrypoint. Zero budget rules out anything without a genuine free
tier. A static host (e.g. GitHub Pages) cannot run this: the app needs a
live Python process, outbound calls to NHTSA/CarAPI/Auto.dev, and a
writable SQLite file, none of which a static site can provide.

## Decision

Deploy to Render using a `render.yaml` blueprint:

- `runtime: docker` builds directly from the existing `Dockerfile`; no
  second deployment config to maintain.
- `plan: free` and `healthCheckPath: /healthz` reuse the health endpoint
  already added in ADR 0006.
- `CARAPI_API_TOKEN`, `CARAPI_API_SECRET`, and `AUTODEV_API_KEY` are
  declared with `sync: false`, so Render prompts for them at setup and
  they are never written into the blueprint file. Leaving them blank is
  valid; the provider registry (ADR 0003) skips them and the app still
  works with NHTSA vPIC and the local structural decoder.
- The Dockerfile's `CMD` now binds gunicorn to `${PORT:-8000}` instead of a
  hardcoded port, since Render (and most container hosts) inject their own
  `PORT` and expect the container to listen on it. The `8000` fallback
  keeps `docker compose up` unchanged for local use.

The free plan has no persistent disk. `VIN_DB_PATH` still points at
`/data/vin_cache.sqlite3`, but that path is ephemeral container storage on
Render, not a mounted volume: the SQLite cache resets on every deploy and
restart.

## Consequences

- One `render.yaml` plus the existing Dockerfile is the entire hosted
  deployment story; no drift between local and hosted configuration.
- The cache reset on restart is accepted rather than worked around. It
  costs some provider quota after a redeploy, nothing more: NHTSA vPIC and
  the local decoder always work without a cache, and CarAPI/Auto.dev
  simply get re-queried. A paid plan with a persistent disk would remove
  this, but that is out of scope for a zero-budget deployment.
- Render's free tier spins the service down after idle periods, so the
  first request after a quiet stretch is slow. Acceptable for a small
  self-serve tool; revisit if usage grows.
