# ADR 0004: Per-field consensus badges and weighted confidence

Date: 2026-07-18
Status: Accepted

## Context

The product USP is accuracy without lying. Free VIN decoders mostly read the
same upstream data (NHTSA vPIC) and silently show blank or wrong fields. We
need a presentation that is honest about certainty per field.

## Decision

Each canonical field gets a badge:

- CONFIRMED: two or more providers agree (values compared case-insensitively,
  numerics normalized).
- SINGLE: exactly one provider reported it, named in the badge.
- CONFLICT: providers disagree; every value is shown with its source.
- UNKNOWN: no provider reported it; rendered as "not available".

Overall confidence is a weighted average over reported fields: CONFIRMED 1.0,
SINGLE 0.5, CONFLICT 0.2; make, model, and year weigh 3, key specs weigh 2,
everything else 1. Buckets: High at 0.8 and above, Medium at 0.5, otherwise
Low. The formula is deliberately simple and shown in a UI tooltip.

## Consequences

- Users see exactly which fields to trust and why, with provenance.
- Consensus never resolves conflicts silently by source priority; that
  alternative was rejected as contradicting the honesty USP.
