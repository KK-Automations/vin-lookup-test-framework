# ADR 0001: Security remediation and history reset

Date: 2026-07-18
Status: Accepted

## Context

The repository leaked live CarAPI credentials through two vectors: a committed
`.env` file on the public GitHub remote, and literal token and secret values
hardcoded as `os.getenv()` argument names in `src/vin_lookup/carapi_auth.py`.
The repo also carried a committed virtualenv (`testenv/`), stray logs, and a
`.gitignore` with overbroad `*.json` / `*.csv` / `*.sqlite3` rules that would
block test fixtures from ever being committed.

## Decision

1. Rotate the CarAPI credentials at carapi.app (owner action; the old values
   are treated as burned regardless).
2. Reset git history to a single clean initial commit of the cleaned tree
   (squash-reinit) rather than surgically scrubbing with `git filter-repo`.
   The prior history (4 commits) carried little value for a portfolio repo,
   and a full reset guarantees no secret survives in any object.
3. Delete `src/` (divergent duplicate of `app/`, including the hardcoded
   secrets), `testenv/`, logs, and scaffolding files.
4. Replace `.gitignore` with a curated list: `.env` stays ignored, `data/`
   (SQLite cache) is ignored, and the overbroad JSON/CSV/SQLite rules are
   removed so `tests/fixtures/**/*.json` can be committed.
5. Ship `.env.example` with empty placeholders as the configuration contract.
   All provider keys are optional; the app degrades gracefully without them.
6. Canonical remote becomes the KP-GENAI organization repository.

## Consequences

- The old public history on the personal remote still contains the burned
  credentials; rotation is what makes them harmless. The personal repo should
  be archived or overwritten.
- Contributors lose blame history prior to the reset. Accepted: single-owner
  portfolio project.
- Every future secret lives only in `.env` (ignored) or deployment secrets.
