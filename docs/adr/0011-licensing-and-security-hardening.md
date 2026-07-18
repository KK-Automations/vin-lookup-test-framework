# ADR 0011: Licensing and security hardening

Date: 2026-07-18
Status: Accepted

## Context

The repository had working security hygiene (ignored `.env`, clean history
after the ADR 0001 reset) but no license, no vulnerability reporting
policy, no third-party attribution for the vendored frontend libraries, no
`.dockerignore`, and no automated secret scanning. For an open source
portfolio project each of these is a baseline expectation.

## Decision

1. **MIT license** for the project. It is the simplest permissive choice,
   matches the vendored libraries (Alpine.js is MIT, htmx is 0BSD), and is
   declared in `LICENSE`, `pyproject.toml`, and the README.
2. **THIRD_PARTY_NOTICES.md** carries the full license texts for the
   vendored htmx and Alpine.js files plus data source attribution: NHTSA
   vPIC is public domain as a US government work; CarAPI and Auto.dev
   responses are fetched under their own terms with user-supplied keys and
   cached only locally, never redistributed.
3. **SECURITY.md** defines private reporting via GitHub Security
   Advisories or email, and documents the secrets handling rules.
4. **`.dockerignore`** excludes `.env`, `data/`, git metadata, and tests
   from the Docker build context. The Dockerfile already copied only
   `app/` and `config/`; this adds defense in depth so a future COPY
   change cannot silently bake secrets into an image layer.
5. **TruffleHog secret scan** runs as a dedicated CI job on every push and
   pull request over the full git history.
6. **Security response headers** (`X-Content-Type-Options: nosniff`,
   `X-Frame-Options: DENY`, `Referrer-Policy:
   strict-origin-when-cross-origin`) are set on every response in the app
   factory. A Content-Security-Policy was deliberately deferred: Alpine.js
   evaluates expressions at runtime and would require `unsafe-eval`,
   which defeats most of the value; revisit if Alpine is replaced with its
   CSP build.
7. The local `.env` was reduced to exactly the variables the app reads,
   removing legacy provider placeholders that caused dotenv parse
   warnings.

## Consequences

- Reusers get clear rights (MIT) and clear third-party obligations.
- A leaked credential now fails CI before it reaches the remote for long.
- The CarAPI keys in the local `.env` predate the history reset and are
  still considered burned until rotated at carapi.app; rotation remains an
  owner action tracked from ADR 0001.
