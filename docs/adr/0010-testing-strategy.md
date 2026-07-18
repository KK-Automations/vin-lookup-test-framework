# ADR 0010: Testing strategy

Date: 2026-07-18
Status: Accepted

## Context

The product's USP is accuracy, so the test suite has to guard exactly the
places where wrong data could leak through: check digit math, field mapping,
and consensus logic. Free provider APIs cannot be hit on every CI run.

## Decision

Three test layers, all pytest with Allure reporting:

- `tests/unit/`: pure domain and engine tests. Check digit against known
  vectors (including the X digit case), model year disambiguation on both
  position 7 branches, typo suggestion generation, all four consensus badge
  states, the confidence formula, and cache repositories against temp
  SQLite files.
- `tests/contract/`: provider mappers run against recorded real payloads in
  `tests/fixtures/<provider>/<vin>.json`. Every mapped field must be
  canonical and clean; placeholder junk (empty strings, "Not Applicable",
  CarAPI paywall notices) must never survive mapping. A small `live` marked
  subset hits the real vPIC API and is deselected by default and in CI.
- `tests/web/`: Flask `test_client` against the app factory with a fake
  provider registry and temp database. Covers page rendering, HTMX
  fragments, the JSON API contract, and error and suggestion flows.

CI runs lint (ruff) and the suite on a Python 3.10 and 3.12 matrix, uploads
Allure results, then builds the Docker image and smoke tests `/healthz`.

## Consequences

- Mapper regressions against real API shapes are caught without network
  access; refreshing a fixture is a one file change.
- The `live` marker keeps an escape hatch for verifying real API behavior
  before provider related releases.
