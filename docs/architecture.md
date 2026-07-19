# Architecture

VIN Lookup is a Flask application that decodes Vehicle Identification
Numbers by cross-checking multiple free data sources and showing the
agreement level for each field. Architectural decisions are recorded in
[docs/adr](adr/), one file per decision.

## System context

```mermaid
flowchart LR
    U[Browser mobile and web] -->|HTMX requests| F[Flask app factory plus blueprints]
    F --> L[Lookup service]
    L --> V[Domain: parse_vin, check digit, model year, WMI, suggestions]
    L --> C[(SQLite cache WAL)]
    L --> R[Provider registry]
    R --> P1[Local structural decoder]
    R --> P2[NHTSA vPIC free]
    R --> P3[CarAPI free tier JWT]
    R --> P4[Auto.dev free tier]
    L --> E[Consensus engine badges plus confidence]
    F --> X[Explorer service makes and models via vPIC]
    X --> C
```

## Lookup sequence

```mermaid
sequenceDiagram
    participant B as Browser
    participant F as Flask
    participant D as Domain
    participant DB as SQLite
    participant T as ThreadPool
    B->>F: POST /partials/lookup (HTMX)
    F->>D: parse_vin (check digit, structure)
    alt invalid VIN
        F-->>B: error_card + suggestion_card (one click retry)
    end
    F->>DB: fresh cached provider responses
    alt stale or missing providers
        F->>T: fan out to those providers (per provider timeout)
        T-->>F: ProviderResults (errors isolated)
        F->>DB: save raw responses
    end
    F->>F: ConsensusEngine.evaluate, badges plus confidence
    F->>DB: record lookup summary for recent list
    F-->>B: vin_result.html fragment (aria-live)
```

## Layers

| Layer | Package | Responsibility |
|---|---|---|
| Domain | `app/domain/` | Pure VIN logic, no I/O: ISO 3779 check digit, model year decoding, WMI tables, parsing, typo suggestions, normalized `VehicleRecord` |
| Providers | `app/providers/` | One module per source behind `VinProvider`; registry filters on available credentials |
| Consensus | `app/consensus/` | Per-field agreement (confirmed, single, conflict, unknown), weighted confidence, provenance |
| Services | `app/services/` | Lookup orchestration (cache, thread pool fan out) and the makes/models explorer |
| Cache | `app/cache/` | SQLite repositories: raw provider responses (30 day TTL), lookup summaries, catalog cache (7 day TTL) |
| Web | `app/routes/`, `app/templates/` | Pages, HTMX partials, JSON API under `/api/v1` |

## Key properties

- Fields no source reports render as "not available"; conflicting sources
  are shown side by side rather than resolved silently.
- Providers without keys are skipped at startup, and a provider failing
  mid-lookup only removes its vote. The local structural decoder
  guarantees a result even fully offline.
- Raw provider responses are cached, so mapper and consensus improvements
  apply to previously fetched VINs without refetching.
- NHTSA vPIC needs no key. CarAPI and Auto.dev are optional enrichment on
  their free tiers, and SQLite is the only datastore.
