# Design

## Context

See proposal.md for motivation and the three capability specs for behavior. There is no application, dependency manifest, or test suite to extend; README.md is a GitLab starter template.

Read-only exploration demonstrated County parcel lookup and geometry queries against City zoning and selected overlay services. For APN 2126-037-055, the observed County geometry intersected `(T)(Q)RD5-1-RIO` over about 99.9953% and `R1-1-RIO` over 0.0011%, and intersected one 2020 building footprint. This is a development observation, not a legal determination or a frozen fixture. Capture the actual responses during implementation and record any differences.

Verified service locations:

| Purpose | Endpoint |
| --- | --- |
| Parcels | https://public.gis.lacounty.gov/public/rest/services/LACounty_Cache/LACounty_Parcel/MapServer/0 |
| Buildings | https://public.gis.lacounty.gov/public/rest/services/LACounty_Dynamic/LARIAC_Buildings_2020/MapServer/0 |
| City boundary | https://public.gis.lacounty.gov/public/rest/services/LACounty_Dynamic/Political_Boundaries/MapServer/19 |
| Chapter 1 zoning | https://zimas.lacity.org/arcgis/rest/services/zma/zoning/MapServer/1102 |
| Chapter 1A zoning | https://zimas.lacity.org/arcgis/rest/services/zma/zoning/MapServer/1101 |
| Historic overlays | https://maps.lacity.org/lahub/rest/services/City_Planning_Department/MapServer/10 |
| Specific plans | https://maps.lacity.org/lahub/rest/services/City_Planning_Department/MapServer/19 |
| Design overlays | https://maps.lacity.org/lahub/rest/services/City_Planning_Department/MapServer/2 |
| Code publisher | https://codelibrary.amlegal.com/codes/los_angeles/latest/overview |

The zoning services expose `ZONE_CMPLT`, `ZONE_CLASS`, and `ZONE_CODE`. County assessor use classification is not legal zoning. Source currency and all applicable code cross-references have not yet been established.

## Goals / Non-Goals

**Goals:** Keep provenance attached to every transformation; isolate slow extraction from lookup; produce deterministic, testable assessments; make external failures explicit.

**Non-Goals:** A general regulatory language, jurisdiction plugin framework, vector database, production authentication, background job platform, or automated legal review. No deployment is part of this change.

## Decisions

### 1. Small application and versioned artifacts

Use `backend/` for a FastAPI application and ingestion command, `frontend/` for React/TypeScript with Leaflet, and `data/` for source manifests, reviewed rules, and labeled fixtures. Use Python standard-library storage/serialization and Shapely for polygon operations. Select maintained dependency versions and lock them during implementation.

The prototype reads versioned JSON files; a database adds little while there are no user accounts, editable projects, or large ingestion corpus. An in-process bounded cache supports repeated GIS reads. Persistent multi-user state and PostGIS belong in the production diagram, not the first implementation. This is a proposed stack choice, not a requirement inferred from the brief's screenshot.

```text
Official text --> source snapshot --> LLM candidates --> validation + review
                                                              |
                                                              v
                                                       reviewed rule set
                                                              |
Address/APN --> County parcel --> City jurisdiction/zoning -----+
                    |                 + selected overlays      |
                    +--> building footprints                   v
                                                  deterministic evaluator
                                                              |
                                                              v
                                                map + cited constraint cards
```

### 2. Resolve parcel identity before assessment

Proposed endpoints: `GET /api/parcels?query=...` returns candidates; `GET /api/parcels/{ain}/context` returns GIS context; `POST /api/assessments` takes a context snapshot identifier, project type, and optional required project inputs. Keep the snapshot server-side in the bounded cache; expiry requires reloading context. Clients cannot supply trusted zoning or rule versions.

Normalize APNs to ten-digit AINs. Query County address fields using escaped, length-limited text and return all matching candidates up to a documented cap; require refinement if capped. Do not send raw user SQL or accept arbitrary upstream URLs. Start with assessor address matching rather than adding a geocoder dependency; unmatched addresses can be retried using APN.

After parcel resolution, request independent GIS layers concurrently with a shared lookup budget below 30 seconds. Check ArcGIS JSON error bodies even on HTTP 200. Respect pagination/transfer-limit flags; incomplete results are unavailable/needs-review, never conclusive negatives. Apply finite request and response-size limits. Cache successes for 15 minutes, expose retrieval time and cache origin, and never silently substitute fixtures for failed live queries.

### 3. Spatial matches are evidence, not legal adjudication

Request output in EPSG:2229 for area/intersection calculations and EPSG:4326 for maps, using the services' reprojection support. Read polygon/multipolygon structure and holes correctly; do not mix coordinate systems. Reject invalid geometry as needing review rather than silently repairing boundaries. Report geometry-derived area as an estimate, not a surveyed legal lot area.

Retain full parcel-to-zone intersections, including boundary touches. For diagnostic labeling only, treat overlap below both 1 square foot and 0.01% of parcel area as a possible sliver. This threshold does not approve a zoning assignment. Multiple positive-area zone matches, unexplained coverage gaps, or conflicting regimes require review. Jurisdiction is similarly based on full parcel coverage; do not infer jurisdiction from postal city or a centroid alone.

The three enumerated overlay checks are a coverage list, not an exhaustive restriction screen. Rule-specific predicates such as hillside/coastal status require separate official evidence or an explicitly labeled user assertion. A cited manual fact entry is sufficient for the small demo cohort; it must retain its source and reviewer. Missing predicates withhold dependent rules.

### 4. Finite rule schema with explicit review

Snapshot selected official sections beginning with LAMC 12.08 and follow the cross-references needed for the five proposed constraint categories. Record source URLs, section anchors, text hashes, retrieval dates, edition/effective-date information, and unresolved references. Confirm source access/reuse terms before retaining excerpts; use operator-provided permitted excerpts if automated retrieval is unavailable. The ICC construction-code page is not needed for this slice.

Represent each rule with ID/version, jurisdiction/regime, supported zone and project predicates, required facts and units, a bounded calculation type, parameters, exceptions, citations, and review state. Implement only the comparisons and arithmetic required by the selected rules; never evaluate model-generated Python or arbitrary expressions. Validation checks source spans, required fields, units, references, and supported operations. A source-span match proves provenance, not correct interpretation, so explicit reviewer approval is still necessary.

Use an operator-run Claude Code extraction step through the user's subscription for this prototype. Before any paid extraction, sanitize inherited Anthropic API authentication/endpoint variables and verify `claude auth status` reports `claude.ai` subscription authentication. If unavailable, report that blocker; do not fall back to API credits or invent an extraction result. Feed only the selected regulatory text and schema; validate the output as untrusted candidate data. Keep extraction outside the application request path. An explicitly labeled recorded extraction supports offline tests, but acceptance also requires a successful real extraction.

Store approved rules and review metadata as versioned artifacts. Detecting a changed source creates new candidates and prevents affected old rules being used as current until reviewed; historical snapshots remain reproducible. Automated continuous source monitoring is deferred.

### 5. Gate applicability, then calculate

Each fact carries value, units, origin, evidence reference, and verification status. Each result carries status, applicable rule version, inputs, value/units if evaluated, derivation steps, citations, and confidence reasons. The response identifies the fact snapshot and rule-set version.

First check jurisdiction, project type, zoning ambiguity, supported zone string, and rule-specific exclusions. Then check missing inputs and evaluate the selected rule. Do not derive legal frontage, lot width, or front/rear orientation from a bounding box. Required dimensions can be entered by the user with units and source attribution; their use limits confidence to medium. Unresolved applicability is undetermined and withholds the calculation. High confidence is reserved for reviewed rules and verified inputs within the stated narrow scope.

All five categories remain visible even when withheld. An assessment with any unresolved category is partial. Unsupported project types receive an unsupported overall assessment with parcel context intact. No result asserts unrestricted buildability or a permit outcome. Changes to user inputs recompute results against the same snapshot; selecting another parcel invalidates pending UI results.

### 6. Acceptance targets and production path

Use pytest for rule, geometry, failure, and API contracts, plus a small browser test for lookup, parcel selection, evidence inspection, and input changes. Capture labeled source responses for reproducible offline runs. Prepare independent calculations from cited passages for at least two supported R1 parcels; do not use the extractor or evaluator as the sole expected-answer generator.

Include the Rhea Court ambiguity case, Chapter 1A, one positive overlay, outside-city, missing-input, invalid-geometry, pagination, and upstream-timeout fixtures. Exercise single-family results and explicit ADU/guest-house unsupported behavior. Measure cached evaluation over 100 runs and report p95 against the one-second target; live service timings are observations, not guaranteed upstream latency.

Document a production diagram with a static frontend, Python API, PostgreSQL/PostGIS for snapshots and spatial indexing, versioned object storage for source evidence, and a separate ingestion/review worker. Show the trust and review boundaries and explain how a new jurisdiction adds source adapters and rule data. Do not build generic plugin machinery or provision those services here.

## Risks / Trade-offs

- GIS alignment artifacts -> preserve intersections and require review rather than silently selecting a zone.
- Incomplete restriction coverage -> expose checked layers and gate every rule on its own applicability evidence.
- Five constraint categories have more exceptions than anticipated -> resolve sources before rule activation; do not declare the change complete with placeholder rules or silently reduce coverage.
- Source or service changes -> store provenance and version hashes, use bounded failures, and maintain reproducible recorded fixtures.
- Old footprint data -> display dataset vintage; do not infer current occupancy, permits, or available building area from it.
- User-supplied dimensions -> validate units/ranges, show origin, and cap confidence.
- LLM extraction errors -> bounded schema, source-span checks, independent examples, and explicit review.
- Narrow building-type coverage -> this change demonstrates the pipeline; future changes must add ADU/guest-house rules before claiming broad brief completion.

## Migration Plan

There is no existing application or data to migrate. Establish local run commands, activate a reviewed rule-set version, and run the offline acceptance suite before the optional live smoke check. Rule-set rollback selects a previously reviewed version only if its sources remain valid; otherwise withhold affected rules. Application rollback is a normal source revision rollback. Deployment remains a separate action.
