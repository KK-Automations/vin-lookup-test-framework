# Security policy

## Reporting a vulnerability

Please report suspected vulnerabilities privately via GitHub Security
Advisories on this repository ("Report a vulnerability" under the Security
tab), or by email to krishnaharshap11@gmail.com. Do not open a public issue
for security reports. You can expect an acknowledgement within a few days.

## Supported versions

Only the latest commit on `main` is supported.

## Secrets handling

- All credentials live in `.env` (gitignored) or deployment environment
  variables. `.env.example` documents the contract with empty placeholders.
- No credential is ever written to source, templates, fixtures, or logs.
  Provider payloads cached in SQLite contain vehicle data only.
- `.dockerignore` keeps `.env`, local data, and git history out of the
  Docker build context.
- CI runs a TruffleHog secret scan on every push and pull request.
- A pre-commit hook (`.githooks/pre-commit`) blocks commits that stage env
  files, key files, or credential-looking strings. Enable it once per clone
  with `git config core.hooksPath .githooks`.
- If you find a leaked credential in this repository, report it privately
  as above; the affected key will be rotated and the artifact removed.
