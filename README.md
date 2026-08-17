# VIN Lookup

**Live: https://vin-lookup-test-framework.onrender.com**

A VIN decoder, search tool, and make/model/year explorer for North America.
Checks each field against multiple independent sources instead of trusting
one, and shows the actual agreement level:

- Confirmed: two or more sources agree
- Single source: only one source reported it
- Conflict: sources disagree, both values are shown
- Not available: nobody reported it, nothing is guessed

Confidence is a weighted average across fields (make/model/year weigh
most), shown with the formula in the UI.

## Features

- ISO 3779 check digit validation. Failures warn, not block, since
  imported vehicles can legitimately fail the North American check.
- Typo correction for illegal letters (I/O/Q) and confusable pairs
  (S/5, B/8, Z/2, G/6, D/0, T/7, A/4), ranked "Did you mean" suggestions.
- NHTSA vPIC (free, no key), CarAPI and Auto.dev (optional keys), plus an
  offline local decoder as fallback. Missing keys just skip that provider.
- Make/model/year explorer back to 1981.
- SQLite caching, no build step frontend (Jinja + HTMX + Alpine.js).
- JSON API with full per-field provenance.

## Quick start

```bash
docker compose up --build
# open http://localhost:8000
```

Or locally:

```bash
pip install -r requirements-dev.txt
flask --app app run
# open http://localhost:5000
```

No keys required for NHTSA vPIC and the local decoder. Copy `.env.example`
to `.env` to add CarAPI or Auto.dev.

## Deploy

Live on Render's free tier via `render.yaml` (Docker blueprint). To deploy
your own: render.com, New > Blueprint, point it at this repo. Free plan has
no persistent disk, so the cache resets on restart; correctness isn't
affected, providers are just re-queried.

## API

```bash
curl https://vin-lookup-test-framework.onrender.com/api/v1/vin/1HGCM82633A004352
```

Returns consensus JSON: per-field status, value, and provenance. Invalid
VINs return `422` with issues and correction suggestions.

## Development

```bash
git config core.hooksPath .githooks   # once per clone: secret guard on commit
pytest
ruff check app tests config
```

## More

- Architecture and diagrams: [docs/architecture.md](docs/architecture.md),
  decision log in [docs/adr/](docs/adr/)
- Security policy: [SECURITY.md](SECURITY.md)
- License: MIT ([LICENSE](LICENSE)); third-party notices in
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
