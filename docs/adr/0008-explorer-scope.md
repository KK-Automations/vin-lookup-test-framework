# ADR 0008: Explorer scope, North America via vPIC catalog

Date: 2026-07-18
Status: Accepted

## Context

Version 1 ships a make, model, and model year explorer alongside VIN decode.
vPIC's `GetAllMakes` returns close to ten thousand registered manufacturers,
most of which are low-volume or commercial and would make a picker unusable.

## Decision

The explorer offers a curated list of about forty consumer makes sold in
North America, ordered alphabetically, plus an "Other" free text input that
accepts any make vPIC knows. Models come from `GetModelsForMakeYear`, cached
seven days per (make, year). Years span 1981 (first standardized 17
character VINs) to next model year.

## Consequences

- The common path is two clicks; the long tail stays reachable through the
  free text input rather than a ten thousand entry select.
- Model data is only as complete as the federal registry; the empty state
  says so instead of implying the make had no models.
