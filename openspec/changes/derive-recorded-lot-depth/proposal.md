# Proposal

## Why
The extractor discards every nonrectangular lot depth even when recorded boundary dimensions and bearings support a deterministic midpoint calculation. Stagg tract 15254 lot 10 exposes this unnecessary restriction.

## What Changes
- Read structured boundary dimensions/bearings and lot-line evidence from recorded tract maps, without deriving numbers from image scale.
- Calculate source-derived approximate depth for a bounded class of straight-sided interior quadrilaterals with effectively parallel side lines and an identifiable opposite rear boundary.
- Validate source identity, geometry, bearings, source references and GIS corroboration; preserve conflicts and exclude ambiguous rear-line, gore, curved, corner/through and multipart cases.
- Surface operands, method, City definition/guidance and remaining legal-lot assumptions with the automatic measurement. Keep existing applicability checks and irregular-envelope withholding.

## Capabilities
### New Capabilities
None.
### Modified Capabilities
- `parcel-context`: Source-derived depth beyond rectangular lots with explicit scope, attribution and rejection behavior.

## Impact
Extraction prompt/validator, deterministic geometry helper, measurement evidence UI, targeted tests and public-source documentation. No APN-specific values in runtime code, new dependencies, general setback-envelope expansion or claim of surveyed/legal verification. Chapter 1 LA definitions apply; other jurisdictions/regimes are excluded from this derivation.
