# ADR 0003: Pluggable provider registry with graceful degradation

Date: 2026-07-18
Status: Accepted

## Context

The product has zero budget, so it depends on free tiers (NHTSA vPIC, CarAPI,
Auto.dev) plus a local structural decoder. Free keys may be absent, rate
limited, or revoked at any time; the app must keep working with whatever is
available.

## Decision

Every source implements `VinProvider` (`fetch` raw payload, `to_record`
normalized mapping) and declares `needs_key`, a `timeout_s`, and
`counts_as_independent`. The registry instantiates the ordered provider list
and filters to those whose credentials are present; a missing key produces a
startup log line, never an error. Provider failures during lookup are
isolated: one provider timing out or erroring only removes its vote.

The local structural decoder is registered as a real provider. It costs
nothing, works offline, and only reports facts the VIN itself encodes (model
year, region, country, curated WMI manufacturer). It never fabricates make or
model.

## Consequences

- The app always produces a result, even fully offline.
- `counts_as_independent` exists because commercial providers often re-serve
  vPIC-derived data; agreement with vPIC then overstates confirmation. The
  UI surfaces `independent_sources` so the accuracy story stays honest.
