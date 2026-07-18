# ADR 0005: Flask with Jinja, HTMX, and Alpine.js; no build step

Date: 2026-07-18
Status: Accepted

## Context

The owner wants to evolve the existing Python codebase with a modern,
maintainable, accessible, mobile-friendly UI, on zero budget, deployable as a
single container.

## Decision

Server-rendered Jinja templates with HTMX for dynamic search and results
(fragments returned from `/partials/*` routes) and Alpine.js for small client
interactions. Both libraries are vendored as pinned minified files under
`app/static/js/`; there is no Node toolchain or build step. Styling is a
single `theme.css` using CSS custom properties (purple design tokens),
mobile-first, honoring `prefers-reduced-motion`.

React and a separate SPA were rejected: two deployables, a build pipeline,
and no benefit at this product size.

## Consequences

- One deployable, instant dev loop, trivially auditable frontend.
- Interactivity is bounded by HTMX patterns; acceptable for search, explorer,
  and result rendering.
