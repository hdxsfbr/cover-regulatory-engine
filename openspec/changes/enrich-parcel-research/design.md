# Design

## Context
Existing immutable context snapshots support concurrent map extraction, scenario persistence and cited Q&A. GIS context acquisition must remain fast. Access probes verified PRISM APN search, ZIMAS landbase APN-to-PIN lookup and profile endpoint, NavigateLA ArcGIS layers, Metro all-stops API and Valhalla pedestrian route API. See the source access report for observations.

## Goals / Non-Goals
Goals: records usable within the assessment, independent loading/retry, durable scenario evidence and no cross-parcel/concurrent-update corruption.
Non-goals: new zoning packages, utility design, title examination, inferred permit finality or automatic statutory transit clearance.

## Decisions
- A small research module owns four adapters using bounded HTTP reads and explicit status envelopes. APIs accept only server-known snapshots and fixed source names, never arbitrary URLs.
- Research is stored separately by a digest of parcel identity and geometry. Each source loads independently with a 24-hour success cache, shorter failure cache and explicit refresh. The browser supplies displayed immutable research IDs on save; the server validates their source and parcel/geometry digest and copies those exact records into the scenario context; map extraction cannot overwrite the separate research store. UI displays saved research when loading a scenario and marks research updates as unsaved evidence.
- ZIMAS uses exact APN landbase matches and retrieves each matched PIN's profile. Planning case links resolve to PDIS and available document metadata with bounded case counts. Multiple PINs remain labeled. Never treat citywide case references as a parcel-specific entitlement.
- PRISM uses book/page/parcel parameters and bounded pagination, retaining record dates, status, type and PDF links. No-records is not legal clearance.
- NavigateLA queries cadastral/easement layers against parcel geometry, and street/sewer context within 100 feet. Spatial relation and layer coverage are explicit; available plan references are retained.
- Metro all-stops is cached globally; nearest candidates are ranked by geographic distance. Up to three pedestrian routes use Valhalla/OSM with bounded sequential calls and caching. Parcel representative point is an estimated origin, not a surveyed entrance. Service frequency and statutory qualification remain unresolved.
- Render a compact summary above expandable source cards. Include timestamps, matching basis, meaningful next actions and source-specific retry. Research is also available to scenario Q&A as source evidence.

## Risks / Trade-offs
- Public endpoints change or fail → bounded reads, schema validation, partial records, retry and original source links.
- GIS and route estimates are not legal instruments → preserve basis and uncertainty, no automatic regulatory check overrides.
- Large histories → bounded pagination with explicit truncation and direct source access.
- Public routing demo has fair-use limits → at most three routes per parcel, serialized calls and cache; production use would require a dedicated provider.

## Migration Plan
Additive records and APIs, no schema migration. Older scenarios without research remain readable and can request research explicitly. Rollback leaves saved JSON harmless.
