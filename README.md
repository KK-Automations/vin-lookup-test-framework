# VIN Lookup

A VIN search, decoder, and make/model/year explorer for North America that
tells you exactly how much to trust every field.

Most free VIN decoders read the same federal database and silently show
blank or wrong values. VIN Lookup cross-checks every decoded field across
multiple sources and labels it honestly:

- **✓ Confirmed**: two or more sources agree
- **⚠ Single source**: only one source reported it, and the badge names it
- **✗ Sources disagree**: every value is shown with its source
- **not available**: no source reported it; we never fill gaps with guesses

An overall confidence score rolls the field badges up with make, model, and
year weighted highest, and the formula is explained right in the UI.

## Features

- **ISO 3779 validation**: full check digit verification, not just a length
  check. Failures warn instead of block, since imported vehicles can
  legitimately fail the North American check.
- **Typo rescue**: illegal letters (I, O, Q) and visually confusable pairs
  (S/5, B/8, Z/2, G/6, D/0, T/7, A/4) produce up to three one-click
  "Did you mean" corrections, ranked by check digit validity.
- **Multi-provider decoding**: NHTSA vPIC (free, no key), CarAPI and
  Auto.dev free tiers (optional keys), plus a local structural decoder that
  works fully offline. Missing keys skip the provider; nothing crashes.
- **Explorer**: browse every model registered with vPIC for any make and
  model year back to 1981.
- **SQLite cache**: repeat lookups are instant and cost zero provider quota;
  raw payloads are cached so decoding logic improvements apply retroactively.
- **JSON API**: `/api/v1/vin/<vin>` returns the full consensus with
  per-field provenance; `/api/v1/makes` and `/api/v1/models` back the
  explorer.
- Accessible, mobile-first purple UI: server-rendered Jinja with HTMX and
  Alpine.js, no build step.

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

No configuration is required: NHTSA vPIC and the local structural decoder
work without keys. To enable the optional providers, copy `.env.example` to
`.env` and fill in CarAPI or Auto.dev credentials.

## API example

```bash
curl http://localhost:8000/api/v1/vin/1HGCM82633A004352
```

```json
{
  "vin": "1HGCM82633A004352",
  "valid": true,
  "check_digit_ok": true,
  "confidence": {"score": 0.643, "bucket": "Medium", "providers_ok": 3, "providers_total": 3},
  "fields": {
    "make": {
      "status": "confirmed",
      "value": "Honda",
      "independent_sources": 1,
      "votes": [
        {"provider": "nhtsa_vpic", "value": "Honda"},
        {"provider": "carapi", "value": "HONDA"}
      ]
    }
  }
}
```

Invalid VINs return `422` with specific issues and correction suggestions.

## Development

```bash
git config core.hooksPath .githooks   # once per clone: secret guard on commit
pytest              # unit, contract, and web tests (live API tests excluded)
pytest -m live      # optional: hit the real NHTSA vPIC API
ruff check app tests config
```

Contract tests run against recorded real provider payloads in
`tests/fixtures/`, so mappers are verified against actual API shapes without
network access.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the system diagrams and
[docs/adr/](docs/adr/) for the architecture decision records, one per
decision, from security remediation through testing strategy.

Layers in short: pure domain logic (`app/domain/`), pluggable providers
behind a registry (`app/providers/`), a consensus engine
(`app/consensus/`), orchestration services (`app/services/`), SQLite
repositories (`app/cache/`), and Flask blueprints (`app/routes/`).

## Security

Credentials live only in `.env` (gitignored) or deployment environment
variables; `.env.example` documents the contract. CI runs a TruffleHog
secret scan on every push. See [SECURITY.md](SECURITY.md) for the
vulnerability reporting policy.

## License

MIT, see [LICENSE](LICENSE). Vendored libraries and data source terms are
listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Vehicle data
decoded from NHTSA vPIC is public domain; CarAPI and Auto.dev responses
are subject to their respective terms of service.
