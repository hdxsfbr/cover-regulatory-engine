# Tasks

## 1. Establish sources and supported examples

- [x] 1.1 Record an official-source manifest for the eight GIS layers and selected LAMC sections, including access/reuse terms, currency, fields, and attribution; verify each required endpoint with a bounded query and document the response or explicit access failure.
- [x] 1.2 Trace LAMC 12.08 and required cross-references for front/side/rear yards, height, and residential floor area; deliver a cited applicability matrix covering required dimensions, hillside/coastal predicates, exceptions, and supported zone strings, with no unresolved dependency marked supported.
- [x] 1.3 Select at least two supported R1 parcels and one each for Chapter 1A, positive overlay, and outside-city outcomes; independently check their context and record evidence plus manual expected calculations for the supported cases.
- [x] 1.4 Capture labeled GIS fixtures for the selected parcels and APN 2126-037-055, documenting differences from the exploration observation; verify fixtures retain geometry CRS, source URL, retrieval time, and enough evidence to reproduce intersections.

## 2. Application foundation and parcel context

- [x] 2.1 Establish Python/FastAPI and React/TypeScript/Leaflet entry points with locked dependencies and local run instructions; verify dependency installation, backend startup, and frontend production build.
- [x] 2.2 Implement bounded ArcGIS query handling and address/APN candidate resolution; verify normalized APNs, ambiguous/no-match inputs, escaped query text, response limits, HTTP-200 error payloads, pagination, and timeouts with adapter tests.
- [x] 2.3 Implement jurisdiction, both zoning regimes, and the three independent overlay checks with provenance and a bounded 15-minute success cache; verify partial failure, no-match, unavailable, cache labeling, and incomplete-result behavior against fixtures.
- [x] 2.4 Implement projected intersections, full zone retention, and diagnostic sliver classification; verify the Rhea Court case, material split coverage, holes/multipolygons, zero-area touches, coverage gaps, and invalid geometry using geometry tests.
- [x] 2.5 Add mapped building retrieval and coordinate conversion for display; verify fixture polygons and 2020 vintage metadata, and ensure failed retrieval differs from an empty building result.
- [x] 2.6 Document context endpoints and source-state semantics alongside the adapter implementation; verify examples against API contract tests and confirm clients cannot provide trusted zoning or arbitrary upstream URLs.

## 3. Regulatory ingestion and reviewed rules

- [x] 3.1 Implement immutable source snapshots and candidate-rule validation using the applicability matrix; verify hashes, section references, source spans, units, unsupported operations, and unresolved references with focused tests.
- [x] 3.2 Add the operator-run LLM extraction command and instructions; verify sanitized Claude subscription authentication before a real extraction, record model/instructions/source versions, and test malformed-output/provider-failure handling without API-key fallback.
- [x] 3.3 Implement explicit rule review and activation with reviewer/time/version metadata; verify unreviewed, invalid, and superseded-source rules cannot be used as current, while historical versions remain readable.
- [x] 3.4 Extract, independently check, and review rules for all five constraint categories; verify each has a cited positive case and an excluded-applicability case matching the independently derived expectations.
- [x] 3.5 Document source refresh, review, and rollback commands; verify a changed source creates a new candidate and blocks affected current evaluation until re-review without overwriting historical evidence.

## 4. Assessment evaluation and API

- [x] 4.1 Implement the finite rule evaluator, fact provenance, unit/range validation, and applicability gates; verify deterministic positive results, missing dimensions, unknown hillside/coastal facts, and unsupported conditions with focused tests.
- [x] 4.2 Assemble per-constraint status, derivation, confidence reasons, and versioned citations; verify user-supplied inputs cap confidence and all five categories remain visible when some are withheld.
- [x] 4.3 Implement the assessment endpoint against server-owned context snapshots; verify expiry, changed project inputs, outside-city and ambiguous zoning gates, and explicit ADU/guest-house/Chapter 1A unsupported outcomes.
- [x] 4.4 Document assessment request/response examples and coverage limits; verify contract examples and confirm identical snapshots, inputs, and rule versions produce identical regulatory results without live model access.

## 5. Assessment interface

- [x] 5.1 Build address/APN entry, candidate selection, project-type selection, and required-input controls; verify keyboard operation, useful validation, ambiguous lookup, and switching parcels while an earlier response is pending.
- [x] 5.2 Display parcel and building geometries with source vintage and textual context; verify the selected parcel matches the result panel and an unavailable footprint source does not hide the parcel.
- [x] 5.3 Build constraint cards and evidence details with citations, derivation, confidence reasons, and checked-source coverage; verify evaluated, partial, needs-review, and unsupported states using a browser test and keyboard inspection.
- [x] 5.4 Add input-change reevaluation, bounded loading, and source-specific retry states; verify late responses cannot overwrite a newer selection and failed live queries never silently show demo fixtures.
- [x] 5.5 Document a short demo walkthrough including supported and ambiguous cases; verify another operator can follow it using the local run instructions and explicitly labeled fixture mode.

## 6. Integrated acceptance and architecture

- [x] 6.1 Run the offline acceptance suite across the selected real parcel fixtures and labeled failure cases for single-family, ADU, and guest-house selections; deliver results showing independent expected values and correct unsupported/review behavior.
- [x] 6.2 Measure 100 evaluations of loaded facts/rules on a documented machine and verify p95 below one second; verify forced upstream timeouts return actionable states within 30 seconds and report a separate live GIS smoke-test result.
- [x] 6.3 Deliver the production architecture diagram and explanation of source versioning, review, PostGIS/storage responsibilities, and jurisdiction expansion; verify it distinguishes implemented components from proposed production additions.
- [x] 6.4 Run backend tests, frontend checks/build, and the browser acceptance path together; verify all spec scenarios are covered by tests or recorded manual checks and report remaining overall-brief gaps explicitly.
