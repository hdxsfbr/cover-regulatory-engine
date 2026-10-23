# Historical POC release report

Superseded for current acceptance by [Current POC validation](poc-validation.md). The Pass labels below describe the historical demonstration gates, not universal successful assessments, zero research effort or instant cold lookup.

2026-10-22. The functional delivery plan implemented the POC feature set, including bounded demonstrations of the six PRD bonuses. This report covers the bounded POC in the primary four-page brief, not comprehensive LA zoning/building-code coverage or a production deployment. All ten functional release gates below pass their stated scope. The original one-week calendar constraint remains unverified because the original project start is not recorded; this report does not claim literal compliance with that historical constraint.

## Requirement matrix

| ID | Result | Implementation and evidence |
|---|---|---|
| P1 | Pass within package scope | Structured summary, governing constraints and design implications; `backend/summary.py`, live workspace and geometry proofs |
| P2 | Pass | Immutable saved scenario requests/results/evidence; save/reopen/compare, process restart and restore proofs |
| P3 | Pass | Conditional values and geometry retain explicit assumptions separately from evaluated results; building-line conflict demonstrated |
| M1 | Pass for defined clean/partial supported cases | Six unseen browser searches needed zero manual dimension transcription or external user source searching. Design choices and remaining professional assertions are counted separately; universal zero regulatory research is not claimed |
| M2 | Pass |22.4 ms visible acknowledgment;6.53 ms loaded HTTP p95 over 100 runs; cold browser outcomes 52.8–66.4 seconds with independent visible jobs |
| M3 | Pass | Same versioned source/fact inputs use the same finite interpreter; boundary, deterministic and source-change regression tests |
| T1 | Pass | Python backend, TypeScript/React frontend; fresh-copy locked install and build |
| T2 | Pass | Actionable AWS-oriented production architecture; cloud hosting is proposed, not deployed |
| S1 | Pass | Actual subscription-backed image reading, source-driven rule extraction and grounded Q&A; retained model/prompt/source provenance |
| S2 | Pass within LA evidence scope | General address/APN search, public GIS, assessor maps and referenced County tract PDFs; no per-address observation prerequisite |
| S3 | Pass | Actual source-derived operator job, unit validation/correction, attributed browser activation; controlled source mutation changes operand 15→17 without formula-fed prompting |
| S4 | Pass | Three explicit bounded packages; coverage/dependency matrix documents excluded branches |
| S5 | Pass | Values carry inputs, source versions, passages, derivation, units, confidence and machine/user provenance |
| S6 | Pass | Typed jurisdiction/regime/project schema; synthetic second-jurisdiction contract test; source adapters and production migration boundaries |
| S7 | Pass | Exact source passages, map crops/full pages, candidate corrections, visible blockers and confidence explanations |
| D1 | Unverified historical timebox | Original project start absent. This execution's corpus freeze and release timestamps are recorded in `release-environment.json`; no invented week-compliance claim |
| F1 | Pass within packages | Actual address→context→background reading→structured assessment flow across frozen holdouts, with retry and bounded partial failures |
| F2 | Pass | Parcel/building map, source vintage, missing-tile/footprint independence; actual setback-map capture |
| F3 | Pass | All three selections across 12+ real parcels; two source-backed positive cases per package plus exclusions. Partial guest-house outputs are explicitly partial, not four resolved dimensions |
| F4 | Pass | Type-specific questions, visible progress/cancel/retry, keyboard/mobile tests and inspected screenshots |
| F5 | Pass | Implemented local components and proposed AWS components separately labeled, with identity, queue, storage, monitoring and restore responsibilities |
| B1 | Pass | Height/area/use inputs, aggregate-floor-area comparison, durable scenario comparison including inputs/evidence versions and geometry status |
| B2 | Pass | Revision/constraint-linked feedback, retained assessment/source references and attributed operator triage; no direct rule mutation |
| B3 | Pass | Actual cited follow-up in API and browser journeys; missing-evidence/fabricated-citation/isolation tests, cancellation and explicit suggested changes |
| B4 | Pass | Browser-verified card→highlighted edge and edge→focused card |
| B5 | Pass within geometry scope | Unequal per-edge clipping, holes/empty outcomes, ambiguous/multipart withholding; provenance-bearing conditional GeoJSON exported in browser |
| B6 | Pass | Token-protected real source fetch/extraction/review/correction/activation, resumable jobs, feedback and eligible rollback |

## Release gates and evidence

Paths in this table are under `data/delivery/` unless stated otherwise.

| Gate | Result and retained evidence |
|---|---|
|1 Generalization | Pass. Frozen 12-parcel corpus plus additional positive cases; six non-Louise holdouts across 3 map books searched through the live browser without authored observations or per-address code. `corpus.json`, `live-browser-holdouts.json`, `holdout-release-report.json` |
|2 Extraction | Pass. 5/6 yield useful cited dimensions; 13 accepted fields, zero accepted value/unit errors against pre-inspected references. Four rectangles have width/depth/area; the other Penfield lot has width only. Glasgow trapezoid correctly has no rectangular dimensions. `reference-readings.json`, `holdout-release-report.json` |
|3 Building types | Pass. `all-project-cohort.json`; backend real-source tests for Stagg/Lemac: main-building rear/height/area, ADU 4 constraints, guest-house rear/separation. Irregular front/side remain withheld. Additional 7745 Louise extraction supplies 62.56 × 163 ft and 10,197.28 sq ft; no address-specific runtime rule |
|4 Synthesis | Pass. `probes/rule-original.json`, `rule-mutation.json`, `operator-live-job.json`, `operator-reviewed-candidate.json`; browser activation capture. Missing foot-unit multiplier rejected then corrected from the quoted source; scope identifiers normalized and dependency dispositions recorded |
|5 Traceability | Pass. Source hashes/passages, exact map pages/crops and machine provenance; `geometry-browser-assessment.json`, `live-setbacks.geojson`; conditional building-line assumptions survive export |
|6 User effort | Pass under the defined criterion. Holdout browser runs have 0 manual dimension transcriptions. Positive ADU examples need 2 design choices (new detached, kitchen); existing-primary and outside-coastal evidence are sourced. Main-building/guest-house examples retain explicit professional applicability/location assertions. No claim that every property needs zero professional review |
|7 Responsiveness | Pass. `ui-acknowledgement.json`: 22.4 ms and visible spinner/disabled button. `http-recalculation-benchmark.json`: 100 runs, p95 = 0.00653 s. `holdout-release-report.json`: maximum full search-to-read outcome 66.404 s, hence observed cold p95 < 120 s; job times30.8–46.6 s. Context has a 25 s server budget and controlled-stall recovery tests. 240 s terminal watchdog/queue/cancellation tests |
|8 Bonus integration | Pass. `live-workspace-proof.json`, `operator-activation.png`, `operator-rollback-proof.json`, `geometry-browser-assessment.json`, `live-setbacks.geojson`, `geometry-desktop.png`, `geometry-mobile.png`, `setback-map.png`; opt-in scripts under `frontend/scripts/` |
|9 Recovery/persistence | Pass. Actual process restart during extraction: `process-restart-proof.json`; saved scenario hashes unchanged. SQLite backup/reopen integrity: `restore-check.json`. Controlled 403/429/timeouts, stale source, malformed model, conflicting observations, late replies and missing geometry tests. Actual publisher 403 retained in `operator-source-fetch-proof.json` |
|10 Delivery | Pass for software/functional artifacts. `clean-install-check.json`; 86 backend tests, 20 browser tests, build and strict OpenSpec validation. Logs `final-*.log`; architecture, API, package, demo, model and persistence docs updated. Historical one-week constraint remains separately unverified |

## What failed during validation and changed

The first supplemental-map readings confused a tract recording page with an assessor page; those readings were rejected and retained. The prompt now labels every source image and distinguishes identities; validation accepts a correctly formatted assessor identifier with explanatory text but still rejects a different book/page.

One full-address search timed out against the County service. Address normalization now handles common suffixes, punctuation/spacing and ZIP+4, and supplies a house-number predicate before the full-address match. Retried holdouts used the same general query path. Source failures remain unavailable; an older success is never silently substituted.

A Vite development-cache failure served an empty module after a source edit. Restarting the development server restored it; production builds and fresh-copy installation passed. Both failed browser attempts and successful reruns remain documented in `attempts/` and release logs.

The operator candidate had an invalid dimensional addition and noncanonical scope labels. Validation rejected activation until those were corrected and attributed. Rejected/ineligible review attempts remain in history. Public source refresh currently receives 403 from the municipal publisher through the direct client; it reports failure and preserves the existing version rather than pretending to refresh.

The new CPD building-line source found a restriction on Louise parcels. Its unresolved effect now blocks the front-yard conclusion without unnecessarily hiding independent side/rear/height/floor-area results. The demonstrated envelope remains visibly conditional.

## Remaining limits, without hidden scope reduction

The PRD permits a small reasoned regulatory subset. Main-building and guest-house packages are bounded to ordinary Chapter 1 R1-1; the selected state-exempt detached ADU branch covers R1-1/RS-1 with an existing single-family primary. Chapter 1A, other zoning variants, attached/conversion/multifamily ADUs and comprehensive construction-code/entitlement determinations remain explicitly outside these packages. Search/evidence acquisition still attempts arbitrary properties.

The ADU handbook is primary agency guidance. Direct state-statute and some publisher requests returned 403; no direct statute verification or newly fetched publisher version is claimed. Effective dates not established by a source remain unknown. Source/implementation review is attributed agent analysis, not independent professional legal or survey validation.

Irregular lots may have useful printed area but no defensible scalar width/depth or envelope. Penfield holdout 2106008016 still has an accepted width only. Generalization acceptance is 5/6 useful maps, not a claim of every dimension on every property.

The application is local and single-user. Operator mutation is token-protected; production still requires project ownership authorization, managed identity, hosted-provider authorization, operational monitoring and deployment. Those boundaries and migration steps are documented in `architecture.md`. No cloud infrastructure was deployed.
