# ADR 0009: Error UX with actionable typo corrections

Date: 2026-07-18
Status: Accepted

## Context

Most failed VIN lookups are typos: the illegal letters I, O, and Q read as
digits, and visually confusable pairs (S and 5, B and 8, Z and 2, G and 6,
D and 0, T and 7, A and 4) swap during manual entry. Generic "invalid VIN"
errors force users to re-inspect all 17 characters themselves.

## Decision

Invalid input produces a specific, plain language explanation (exact length
entered, which illegal letter appeared and what it probably was) plus up to
three "Did you mean" candidates. Candidates come from substituting illegal
letters and from single position confusion pair swaps, ranked by whether the
corrected VIN passes the ISO 3779 check digit. Every candidate is a one
click button that immediately re-runs the lookup. Check digit failures on
otherwise well formed VINs warn rather than block, because imported vehicles
can legitimately fail the North American check.

## Consequences

- The correction search space is deliberately narrow (single position swaps,
  known confusion pairs) so suggestions stay trustworthy; we never suggest a
  VIN that is merely plausible.
- Corrections that pass the check digit are labeled so users understand why
  the suggestion is confident.
