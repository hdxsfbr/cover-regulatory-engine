# Acceptance evidence

The fixtures were acquired from official services on 2026-10-21/22 (local/UTC). Raw returned geometries, queries, URLs, timestamps, statuses and EPSG:2229 metadata are retained. The map copy is EPSG:4326. No fixture geometry has been snapped, buffered or repaired. These are recorded GIS observations, not surveyed legal determinations. Failed queries remain failed in their labeled fixture.

## Real parcel contexts

| AIN | Recorded address | Jurisdiction | Zoning evidence |
| --- | --- | --- | --- |
| 2126037055 | 6754 RHEA CT LOS ANGELES 91335 | Los Angeles | needs-review: (T)(Q)RD5-1-RIO (99.995308%); R1-1-RIO (0.001071%) |
| 2202010005 | 7543 LOUISE AVE LOS ANGELES CA 91406 | Los Angeles | needs-review: R1-1 (99.994535%) |
| 2202010006 | 7537 LOUISE AVE LOS ANGELES CA 91406 | Los Angeles | needs-review:  |
| 2202010009 | 7523 LOUISE AVE LOS ANGELES CA 91406 | Los Angeles | resolved: R1-1 (100.000000%) |
| 2202010010 | 7517 LOUISE AVE LOS ANGELES CA 91406 | Los Angeles | resolved: R1-1 (100.000000%) |
| 4103012026 | 6901 KNOWLTON PL LOS ANGELES CA 90045 | Los Angeles | needs-review: R3-1 (99.898531%) |
| 4328021043 | 9601 CHARLEVILLE BLVD 16 BEVERLY HILLS 90212 | outside-city | needs-review:  |
| 5138014112 | 1111 S HOPE ST LOS ANGELES CA 90015 | Los Angeles | needs-review: [HB3-SH1-5][CX3-FA][CPIO-O] (99.999247%) |

The two positive contexts, 2202010009 and 2202010010, were independently checked by comparing full parcel polygon coverage with City boundary and zoning geometry. Both have one R1-1 zone covering the entire parcel, no positive Chapter 1A overlap and complete no-match results in the three selected overlay layers. The acceptance tests independently recompute these intersections from raw recorded responses. This verifies the GIS context, not all project-specific applicability conditions.

Rhea Court 2126037055 retains the two zones from exploration: dominant (T)(Q)RD5-1-RIO at about 99.9953% and R1-1-RIO at about 0.0011%, with a small uncovered remainder. Its smaller overlap is below both sliver thresholds; it is not discarded. The new observation agrees with the exploration to the reported precision and still needs review. 2202010005 is a separate single-zone coverage-gap example. 2202010006 preserves partial upstream failure.

4103012026 has a positive Specific Plan match (Los Angeles Coastal Transportation Corridor), which gates calculations even apart from zoning ambiguity. 4328021043 is outside LA City based on boundary geometry, not postal text. 5138014112 has only positive Chapter 1A evidence and an approximately 0.000753% coverage gap: calculations are unsupported, and the gap remains unresolved.

## Independent numeric scenarios

The following design dimensions and applicability assertions are **hypothetical**, not parcel measurements or verified entitlement facts. They exercise the positive rule path against real GIS contexts. A professional project survey and approval review were not supplied. All results therefore have medium confidence. A separate synthetic trusted-fact test checks the high-confidence code path without asserting that the real sites have verified facts.

| Scenario | Depth / width / area / building height / uniform roof slope | Front | Side, each | Rear | Height cap | RFA cap |
| --- | --- | --- | --- | --- | --- | --- |
| A, context 2202010009 | 80 ft / 40 ft / 6000 sq ft / 18 ft / 20% | 16 ft | 4 ft | 15 ft | 28 ft | 2700 sq ft |
| B, context 2202010010 | 120 ft / 50 ft / 7500 sq ft / 28.1 ft / 25% | 20 ft | 7 ft | 15 ft | 33 ft | 3375 sq ft |

Independent derivation from preserved LAMC passages (not extractor output):

- 12.08 C.1: A uses 20% of 80 = 16, below the 20-foot cap; B uses 24 capped at 20.
- 12.08 C.2(a)-(b): A's 40-foot width permits 4 feet, above the 3-foot floor; no increment at 18 feet. B has a 5-foot base plus two one-foot increments for 10.1 feet above 18, giving 7.
- 12.08 C.3: both ordinary main-building rear yards are 15 feet.
- 12.21.1: A's uniform uppermost roof slope is below 25%, giving 28 feet; B meets 25%, giving 33 feet.
- 12.08 C.5(a): 45% of 6000 = 2700 and 45% of 7500 = 3375. The complete 12.03 definition governs counted Residential Floor Area. This does not calculate the proposal's counted area or an encroachment envelope.

Every scenario asserts the specified ordinary-lot, non-hillside/coastal, frontage, side-wall/deck and height-exception conditions. Leaving the relevant assertion unknown withholds the value. Each category has an excluded-applicability test. Both unsupported project selections retain all five cards and parcel evidence.

## Test coverage

`test_core.py` covers APN normalization, address escaping, body/deadline limits, HTTP-200 ArcGIS errors, incomplete pages, malformed features, holes/multipolygons, touches, slivers, gaps, conflicting regimes, unknown jurisdiction, independent overlay failures, unavailable buildings, map coordinates and cache provenance.

`test_acceptance.py` covers the real cohort, independent numeric expectations, all five unknown-applicability cases, missing dimensions, user provenance/confidence, synthetic verified evidence, overrides, unsupported project/zone outcomes, source spans/units/operations, rejected and tampered rules, dependency supersession, immutable refresh under provider failure, subscription-only authentication, malformed model output, deterministic API examples and trust boundaries.

`frontend/tests/assessment.spec.ts` follows lookup, candidate choice, keyboard evidence controls, input updates, medium-confidence calculations, unsupported projects, stale response protection, Rhea/Chapter 1A outcomes and failed footprints with parcel mapping intact.

Performance evidence is in `data/benchmark.json`; rerun with `uv run python -m backend.benchmark`. The 100-run test evaluates loaded facts/rules without network or LLM calls and asserts p95 below one second. Live GIS timing and bounded timeout evidence are recorded separately below.

## Scenario traceability

| Spec scenarios | Verification |
| --- | --- |
| Formatted APN; ambiguous address; failed lookup | `test_inputs`, `test_api_full_contract`, `test_timeout_and_body_limit`, browser candidate-selection path |
| Postal address differs; boundary uncertainty | Real outside-city fixture; `test_invalid_geometry_and_jurisdiction`, boundary gap tests |
| Rhea Court sliver; two zoning regimes | `test_real_rhea_overlay_outside_and_variation`, `test_boundary_touch_gap_and_multiregime` |
| Partial overlay failure; historic/missing footprints | `test_partial_source_and_footprint_states`, `test_fixture_provenance_and_map`, browser failure path |
| Source changes; superseded source | `test_refresh_immutable_and_failure_invalidates_old_rules`, `test_rule_validation_and_review` |
| Extract a dimensional rule; invalid model output | Preserved actual Claude extraction and resolved candidate; schema/units/operations/quotes tests |
| Incomplete exception handling; supported rule set; R1 variation | Rejected original candidate; all five positive and unknown-applicability tests; R1-1-RIO gate |
| Provider unavailable | Subscription/malformed-output/provider-timeout test; refresh provider-failure test; existing active set retained |
| Missing lot width; updated project input | `test_missing_dimensions_and_user_evidence`, API contract and browser height update |
| Supplied dimensions; complete verified evidence | Both independent scenarios return medium; synthetic attributed trusted-fact path returns high |
| Unsupported building type; overlay found; unknown hillside | Real overlay + both unsupported project tests; each category's missing applicability test |
| Inspect a result; context changes during lookup | Browser keyboard evidence, citations and delayed-response race tests |
| Slow upstream source | Real request timeout plus measured 25-second forced stall in `data/lookup-timings.json`; visible source error and retry control |
| Reproducible acceptance run | Backend fixture suite and browser suite with external requests blocked; optional map tiles/fonts are not needed for the evidence |

## Overall brief boundaries

This delivers the scoped first change, not all building types in the broader brief. ADU and guest-house rules, Chapter 1A calculations, complete overlays, construction-code compliance, surveyed dimensions, automatic legal lot/frontage determination, massing/setback geometry, professional legal review and production deployment remain outside this implementation. The UI and API explicitly identify those limits rather than presenting a complete buildability answer.

## Recorded final run

- Backend: **37 tests passed**. One dependency deprecation notice remains in Starlette's httpx-based TestClient; it does not affect the tested behavior.
- Frontend: TypeScript checks and production build passed; **3 browser acceptance tests passed** with external requests blocked.
- Loaded evaluation: **0.713 ms p95** over 100 runs on Intel Core i9-14900KF, Python 3.11.13, Linux x86_64. Exact measurements and rule version are in `data/benchmark.json`.
- Live APN 2202010009: initial 10-second source timeout withheld zoning while retaining seven successful sources. With a 22-second per-request allowance under the unchanged 25-second total budget, the retry completed in **10.41 seconds**, resolved R1-1/LA City and returned all eight source outcomes successfully. Exact statuses are in `data/lookup-timings.json`.
- Forced indefinitely stalled transport: **25.03 seconds** to actionable unavailable states, below the 30-second target; no fixture fallback.
- Visual inspection: desktop screenshot shows parcel and footprint outlines, readable source facts, all five constraint cards and attributed input controls. Map tiles are optional; geometry and textual evidence remain usable when external tile access is blocked.
- OpenSpec strict validation and Python unused/undefined-name checks passed.
