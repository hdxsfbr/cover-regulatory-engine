# API contract

`GET /api/config` returns live/fixture mode, labeled applicability checks and numeric bounds. No secrets are returned.

`GET /api/parcels?query=2202-010-009` normalizes the APN and returns `status`, `features[].properties` (AIN, APN, SitusFullAddress) and source provenance. Address text is escaped, uppercase substring matching, not geocoding. Maximum query length is 160 characters; wildcards are rejected. Up to 21 candidates may be returned. The caller must choose a candidate. A transfer-limit flag means unavailable/incomplete and asks the user to refine; the adapter does not treat a truncated page as a complete set or automatically enumerate unbounded pages.

`GET /api/parcels/2202010009/context` returns a UUID `snapshot_id`, parcel attributes, jurisdiction, zoning status, complete zone matches (including area, fraction, possible sliver and boundary touch), map GeoJSON, issues, selected overlays and independent source records. Server-owned snapshots last 15 minutes; at most 100 are retained. The separate successful GIS cache also lasts 15 minutes and retains at most 100 entries. Cached reads keep the original retrieval time and change `origin` to `cached`.

Every GIS record includes source URL, retrieval timestamp, dataset vintage (or unknown), origin and EPSG:2229 CRS. Raw parcel/zoning intersections use US survey feet. Map GeoJSON uses longitude/latitude EPSG:4326. Estimated polygon area is not legal surveyed lot area. Footprints are the 2020 LARIAC dataset.

| Source state | Meaning |
| --- | --- |
| matched | Complete response containing features; spatial evidence still requires interpretation |
| no-match | Complete query with zero features in that layer only |
| unavailable | HTTP/ArcGIS error, deadline, invalid body, oversized body, or incomplete page |
| not-checked | Parcel unresolved, so this downstream layer was not queried |

All eight configured layers are fixed server-side. Clients cannot supply trusted zoning, arbitrary upstream URLs, verified facts or rule versions. Geometry errors and unaligned boundaries withhold zoning resolution. A parcel matching only Chapter 1A evidence is unsupported even if a coverage gap remains; the gap is still displayed. Mixed regimes remain ambiguous.

A lookup has a 25-second shared budget; individual upstream requests default to 22 seconds (search 12). Responses are limited to 16 MB. Independent completed responses survive a timeout. A failed source is displayed separately; explicit refresh retries the entire context without reusing cached evidence.

`POST /api/assessments` accepts:

```json
{
  "snapshot_id": "UUID returned by the context endpoint",
  "project_type": "single-family",
  "inputs": {"lot_depth_ft": 80, "lot_width_ft": 40, "lot_area_sqft": 6000, "building_height_ft": 18, "roof_slope_percent": 20},
  "checks": {"ordinary_context": true, "outside_hillside_coastal": true, "frontage_reviewed": true, "side_conditions_reviewed": true, "height_conditions_reviewed": true},
  "evidence_note": "Hypothetical test scenario; not measured site dimensions or verified applicability"
}
```

This scenario against recorded APN 2202010009 returns `status: evaluated` with five ordered constraints: front 16 ft, side 4 ft each, rear 15 ft, height 28 ft, residential floor-area cap 2700 sq ft. All are medium confidence because the inputs/checks are user supplied. Each carries reasons, input origin/evidence, derivation, rule version, exact source quotations/hashes and public links. The response identifies the rule-set version and snapshot. Changes to inputs recompute against that same snapshot without any LLM call.

Missing inputs or checks yield `needs-review` with null values; overall status is `partial`. Unsupported projects (ADU/guest-house), outside-city parcels and unsupported zoning yield `unsupported`. All five cards stay present. Numeric inputs must be finite, in the advertised ranges and use the named units; strings/booleans are not numeric inputs. Checks must be booleans. Unknown fields are rejected. Validation errors return 422; absent/expired snapshots return 410 with reload instructions.

Examples are exercised in `backend/tests/test_acceptance.py::test_api_full_contract`. Interactive schema is at `/docs` and `/openapi.json`.

## Source recovery

`GET /api/parcels/{ain}/context?fresh=true` is an explicit whole-context refresh. In live mode it evicts that parcel's prior success cache, queries official sources within the same 25-second budget, and creates a new immutable server-owned snapshot. A failed fresh read stays failed; it cannot resurrect a previous cached success. Existing snapshot IDs retain their old evidence until normal expiry/eviction. Recorded mode replays its saved records with new diagnostic explanations; `fresh=true` never makes an upstream request in that mode.

`diagnostics` adds entries such as:

```json
{"code":"source_unavailable","message":"Chapter 1 zoning source unavailable; its evidence is missing. Refresh parcel sources to try again.","sources":["Chapter 1 zoning"],"retryable":true}
```

Codes distinguish `source_unavailable`, `source_not_checked`, `parcel_unresolved`, `invalid_geometry`, `jurisdiction_boundary_gap`, `zoning_no_match`, `zoning_multiple_matches` and `zoning_coverage_gap`. `issues` retains the equivalent readable messages for existing clients. A missing zoning source alone is not a coverage gap or zoning conflict. No-match/gap diagnostics require complete zoning queries; returned multiple positive matches are retained even alongside a source failure.

`applicability_fingerprint` is an opaque server-computed comparison value for complete resolved applicability evidence, or null when that evidence cannot be confirmed. It includes parcel/boundary/zoning/selected-overlay features, CRS and statuses, excluding response timestamps, feature ordering, cache origin and building footprints. It is not proof of legal applicability. The UI preserves same-parcel inputs and assertions only when evidence is comparable and unchanged; changed/null evidence clears assertions with an explanation, retains dimensions and their user-supplied note, and reassesses only the new snapshot. Fresh failures never relabel prior evidence as current. Expiry and early parcel failure retain a selected identifier for recovery.

For screen rendering, `GET /api/parcels/{ain}/context?compact=true` omits raw `features` and upstream `query` from each source record. The map, diagnostics, source URLs/statuses/timestamps, zone matches and fingerprint are unchanged. The default response remains full for existing clients. Full raw records are retained in the server-owned snapshot for assessment and reproduction; compact mode changes only the transmitted representation. The browser combines this with `fresh=true` on explicit refresh.

## Public parcel evidence

Context adds `document` (map ID, AIN, legal description, status, source URL,
retrieval time, SHA-256 content hash, origin and known vintage) and `observations`.
Document states are available, unavailable and unreferenced. PDF retrieval is
limited to 10 MB, 12 seconds and approved HTTPS County redirects, within the
existing 25-second context budget. Successful PDFs are retained by hash.

Observation records include fact key, value/units, tract/lot, page/location,
method, document hash and attributed transcription review. Status is reviewed,
stale or conflict; none means independently verified legal applicability.
`POST /api/assessments` accepts optional `observation_ids` (at most three) from
that snapshot. Acceptance supplies dimensions without transcription and remains
user-attributed/medium confidence. Do not also send a numeric override for the
same key: deselect its observation first. Unknown/stale/conflicting IDs fail 422.
Legacy inputs, checks and evidence_note remain supported. Client verification
metadata is rejected. Snapshots retain the full evidence; compact context keeps
summaries, observations and references.

Constraints add `blockers`: code, message, target, action and label, alongside
legacy reasons. Unsupported scope takes precedence over missing-input prompts.
Source failures have retry actions; dimensions/design/checks target their controls.
New evidence versions participate in applicability comparison: changed/unknown
sources invalidate acceptance, unchanged evidence retains it. Typed dimensions
and notes are preserved on refresh as user inputs, not promoted to verified facts.

## Full workspace and background processing

`POST /api/evidence-jobs` accepts `{snapshot_id,retry:false}` and returns a durable job. `GET /api/evidence-jobs/{id}` reports status/stage/error/result; `POST .../{id}/cancel` is terminal. Operator jobs require the Bearer operator token even when read through this route. `POST .../{id}/context` accepts the current `snapshot_id` and merges a completed matching map job into a new immutable context. A changed parcel/document or invalidated snapshot returns409. Automatic observations contain source hash, URL, page, normalized region, units, method and a machine-corroborated provenance tier.

`GET /api/documents/{sha256}/pages/{page}` validates the original hash and renders a stored PDF page. Pages1–8 are allowed; arbitrary URLs and filesystem paths are not accepted.

`GET/POST /api/projects` lists/creates local projects (`name,snapshot_id`). `GET /api/projects/{id}` returns its context and saved revisions. `POST /api/projects/{id}/scenarios` accepts an assessment request plus `name`; it saves the complete request/result/context as an immutable revision and rejects a different parcel. Saving again creates a revision, not an overwrite. Reopened assessments use retained context; new source research requires explicit refresh. Previously saved result values remain historical, rather than being recomputed in place with newly activated rules.

`POST /api/scenarios/{id}/questions` accepts `{question}` and returns a bounded, cited answer grounded only in that saved revision. Evidence IDs and exact quotes are validated. Client disconnection/cancellation signals the provider process; no suggested change is applied automatically.

`POST /api/feedback` accepts `{scenario_id,category,comment}`. It persists the exact assessment and source/rule references. Feedback cannot promote a fact or activate a rule. Operator triage appends attributed reviewing/resolved/rejected events; retrieval returns the latest status and history.

## Operator boundary

All `/api/operator/*` routes require `Authorization: Bearer <local operator token>`. `/sources` returns retained source versions and passages; `/packages` returns current packages/activation history; `/jobs` exposes resumable source/extraction jobs. `/refresh` fetches a configured municipal section. `/extract` accepts selected source hashes and a scope, then queues actual source-derived model extraction. Neither endpoint simulates completion.

`POST /reviews` requires a completed extraction job, corrected candidate, reviewer, decision(review/reject) and rationale. Schema/unit/source-span/unresolved-dependency validation prevents approval of invalid candidates. `POST /reviews/{id}/activate` repeats eligibility/current-source/validity-interval checks and records an activation event. Reactivating a prior eligible review is rollback; superseded sources prevent rollback to an ineligible version. `/feedback` and `/feedback/{id}` support attributed triage.

This local POC has no multi-user project ownership boundary; production must add it before exposing project APIs. See the architecture handoff for the authentication and persistence migration.

Supplemental research: `POST /api/research/{planning|permits|engineering|transit}` with `{snapshot_id, fresh?: boolean}` returns independently acquired records and an immutable ID. Scenario saves may include `research_ids: {source: id}` to capture displayed research. The server checks parcel/geometry association. See [supplemental-research.md](supplemental-research.md) for source coverage, cache behavior and bounds.
