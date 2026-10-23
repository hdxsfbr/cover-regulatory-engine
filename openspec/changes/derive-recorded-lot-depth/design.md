# Design

## Context
See proposal.md. Current extraction accepts width/depth only for rectangles. County maps establish Stagg lot 10's unequal sides; LAMC 12.03, City Planning ZI2391 p24 and LADBS Zoning Manual printed p31 explain depth and rear-line interpretation. The latter distinguishes an identifiable opposite approximately parallel rear line from a 10-foot chord in gore-shaped cases.

## Goals / Non-Goals
Compute a defensible source-derived approximate depth, retaining legal interpretation assumptions. Do not guess from GIS/image scale, broaden setback envelopes, infer all irregular-lot widths, or certify current legal boundaries.

## Decisions
- Extend the existing image prompt with optional recorded-boundary operands and citations. The model reads and classifies evidence; Python parses bearings and calculates the midpoint distance.
- Bound support to a convex four-sided interior lot with straight frontage/rear, essentially parallel sides and an opposite approximately parallel rear boundary. Angular/closure limits are conservative automation limits, not legal definitions.
- Compare depth and side measurements with EPSG:2229 parcel geometry. Report transverse boundary discrepancies explicitly rather than treating a GIS width as a recorded width. Gross disagreement rejects derivation.
- Preserve the existing automatic-observation contract and append regulatory citations/operands/assumptions. Add UI display for those fields. Ordinary-context/frontage assertions remain required by regulatory evaluation; no derived envelope for irregular lots.
- Include derivation version in extraction prompt/cache identity. Existing saved scenarios remain historical; refresh starts a new result.

## Risks / Trade-offs
- Rear-line interpretation depends on surrounding lots → require recorded classification evidence, withhold ambiguous/gore/corner/through cases and retain assumption in every derived result.
- Historic record versus current GIS mismatch → report discrepancy, reject substantial disagreement and never label result legal verification.
- Model reading errors → independent pre-read Stagg operands, numeric/bearing/geometry validation and negative tests.

## Migration Plan
No database migration. Existing result schema is additive. Run targeted and full backend tests, browser evidence test and a real general extraction for Stagg; restart local API to load changes.
