# ADR 0014: Rebrand to Honest VIN

Date: 2026-07-28
Status: Accepted

## Context

The name "VIN Lookup" and the URL `vin-lookup-test-framework.onrender.com`
said nothing about what the product actually does differently. Competitor
research this session confirmed the real gap: paid sites (Carfax,
AutoCheck, ClearVin, VINAudit, Bumper) sell vehicle history reports
(accidents, title, odometer) behind a subscription, a different product;
free decoders (NHTSA, vininfohub) do spec decoding but trust one source
blindly with no way to flag a wrong or missing field. This app's actual
edge is free spec decoding with honest, per-field, multi-source
confidence, and the old name and the footer disclaimer didn't say so.

## Decision

1. **Name: Honest VIN.** Chosen over "VINtegrity" and "VIN Truth" as more
   direct while still reading as a name rather than a generic label.
2. **URL: rename the Render service slug to `vin-truth`,** giving
   `https://vin-truth.onrender.com`. Not a purchased custom domain, kept
   consistent with the zero-budget approach used for every other hosting
   decision in this project (ADR 0006, ADR 0012).
3. **Rewrote the footer disclaimer** to explain the niche positively
   instead of restating the mechanism: it names what paid history reports
   and free decoders each fail to do, then states what this app does,
   without any "not a..." self-negation or em dashes.
4. **Full rebrand in one pass:** header wordmark, page titles, README,
   and deployment config (`render.yaml`, `pyproject.toml`, Dockerfile,
   CI) all updated together rather than leaving the product half-renamed.

Render's free `onrender.com` subdomain is fixed at service creation and
cannot be renamed afterward. The dashboard's Settings > Name field is
only a display label; changing it does not touch the actual URL slug,
confirmed by editing it directly and finding the live URL unchanged
(also documented on Render's own community forum). The only way to get
`vin-truth.onrender.com` is to delete the existing service and create a
fresh one from this repo's `render.yaml`, which now has `name: vin-truth`
so the new service provisions with the right slug from the start.

Not touched: the GitHub repository name (`vin-lookup-test-framework`), a
much larger and URL-breaking change nobody asked for; the `vin_lookups`
SQLite table name, a schema identifier rather than brand text; ADRs
0001-0013, rewriting historical decision records to match a later rename
would be revisionist; the favicon binary, no new logo was requested.

## Consequences

- The name and URL now describe the actual differentiator (honest,
  multi-source, free) instead of a generic label.
- Recreating the service means a few minutes of downtime, losing the old
  service's deploy history and logs, and re-adding the CarAPI and Auto.dev
  environment variables from scratch. The old
  `vin-lookup-test-framework.onrender.com` slug becomes unreachable once
  the old service is deleted; Render does not redirect an old slug to a
  new one, so any existing links to the old URL will break rather than
  forward.
