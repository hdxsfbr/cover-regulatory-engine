# Tasks

The requirement IDs and release gates in docs/prd-delivery-plan.md govern completion. These tasks are the full requested delivery scope, including all six bonus features. Do not replace generalized behavior with prewritten parcel data or count an unsupported project label as a positive package. Tests and docs land with each workstream; final checks validate integration.

## 1. Acceptance baseline and feasibility (P1, M1, S1–S4, F3, D1)

- [x] 1.1 Freeze a 12+ real-parcel corpus and six non-Louise holdouts across three map books, including irregular/corner, constrained, ambiguous and outside-city controls; record provenance and independently transcribed expected map readings, and verify holdouts are absent from authored observations/extractor examples.
- [x] 1.2 Prove a supported subscription-authenticated model invocation can identify a new lot and return page/region-grounded observations from a scanned map; record auth/model/prompt/source and timing, test malformed/ambiguous output and provider failure, and document the adapter contract without API-credit fallback.
- [x] 1.3 Prove source-driven regulatory extraction without expected thresholds/formulas in the prompt; retain original and changed-source candidate runs, verify units/citations/dependencies and changed operands, and document any feasibility blocker and its schedule impact.
- [x] 1.4 Acquire current primary-source definitions and dependencies for the selected single-family, detached ADU and guest-house packages; publish the branch/source/precedence matrix with dates and exclusions and verify each package has a feasible positive evidence path before further UI expansion.

## 2. Persistent evidence and general acquisition (P2, S2, F1, M2)

- [x] 2.1 Add SQLite project/job/evidence references and versioned migrations while retaining hashed originals; test import of existing artifacts, atomic writes, restart and rollback, and document the local data/backup layout.
- [x] 2.2 Implement bounded durable evidence jobs with deduplication, cancellation, source/version keys and explicit stages; verify stalled sources/models terminate within budgets, restart does not lose completed work, and progress/API behavior is documented.
- [x] 2.3 Generalize address normalization/candidate selection and document discovery from parcel, map and tract/record identities; verify unseen-address acquisition, missing references, 403/429/timeouts and approved-host/page/byte limits without seed lookup or live fixture fallback.
- [x] 2.4 Implement text/rendered-page extraction with lot identification, page-region references, units, ditto interpretation and explicit ambiguity; validate against development map examples and negative wrong-lot/illegible cases, and document extraction provenance and limits.
- [x] 2.5 Add deterministic observation validation/corroboration for dimensions, area, geometry and edge orientation; test rectangles, clipped/corner/irregular cases, conflicting documents and changed hashes without promoting machine extraction to legal review.
- [x] 2.6 Integrate the sourced applicability facts identified by the matrix, splitting broad assertions into individually attributable predicates; verify true/false/unknown/conflict outcomes, preserve dataset coverage limits and document which genuine project/interpretation inputs remain.

## 3. Source-driven rule packages (S3–S6, F1, F3, M3)

- [x] 3.1 Generalize the typed rule schema/interpreter for reviewed expressions, jurisdiction/regime/project identity, dates, exceptions and dependencies; test unsupported operations, unit errors, deterministic replay and a synthetic second jurisdiction, with schema documentation.
- [x] 3.2 Replace formula-fed extraction with source-driven candidates and dependency resolution; verify citation spans, cross-reference/precedence review, source supersession and explicit activation, retaining reproducible model and review evidence.
- [x] 3.3 Migrate and revalidate the single-family package against its source-defined operands and fact predicates; pass existing numeric boundaries plus at least two positive source-backed project scenarios and explicit excluded branches, documenting any corrected interpretation.
- [x] 3.4 Implement the selected new detached ADU package with sourced use/eligibility, precedence, dimensional/area constraints and exceptions; pass two independent source-based positive scenarios and exception/unsupported variants, publishing the exact coverage matrix.
- [x] 3.5 Implement the selected detached guest-house package with sourced classification, use limitations and dimensional constraints; pass two positive scenarios plus misclassification/exception cases and prove it is not a renamed single-family or ADU fallback.

## 4. Assessment workspace and scenarios (P1–P3, M1–M3, F1, F4, B1)

- [x] 4.1 Add durable project/scenario APIs with immutable evidence/rule references and revision-scoped requests; test save/reopen/restart, source changes, input validation and two-project isolation, documenting backward compatibility and migration.
- [x] 4.2 Implement structured summaries, proposed-design implications and explicitly conditional decision branches; verify useful partial answers, assumption attribution, confidence reasons and no unconditional numeric leakage when applicability is unresolved.
- [x] 4.3 Build type-specific project questions, progressive evidence/job states and source passage/map-crop inspection; verify an unseen-property flow uses automatically obtained facts without external source hunting or manual transcription in clean supported cases.
- [x] 4.4 Add saved scenario comparison and dependency-aware recalculation; verify changed height/area/use updates only applicable outputs, preserves prior snapshots, and achieves loaded p95 below one second over 100 recorded runs.
- [x] 4.5 Validate the workspace's keyboard/mobile and recovery behavior; test cancellation, late responses, missing tiles/footprints, refresh failures and unsaved-work preservation, and document inspected screenshots and remaining review effort.

## 5. Regulatory map and geometry (F2, B4, B5)

- [x] 5.1 Implement source-backed front/side/rear edge classification for the supported lot cases; verify orientation independently on rectangular and corner/irregular examples and withhold ambiguous classifications with a specific reason.
- [x] 5.2 Generate setback regions from applicable per-edge rules in the correct projected CRS; verify expected geometry for unequal setbacks, clipped boundaries, holes, multipart/empty outcomes and invalid geometry, and document the envelope's scope.
- [x] 5.3 Link map annotations and constraint cards and add provenance-bearing GeoJSON export; browser-test both selection directions and conditional labels, inspect desktop/mobile rendering, and verify exported units/CRS/versions and coordinates.

## 6. Grounded follow-up and feedback (B2, B3)

- [x] 6.1 Implement revision-scoped evidence retrieval and a bounded model Q&A endpoint using the authorized adapter; test cited supported answers, missing evidence, fabricated-citation rejection, malicious source instructions, cancellation and cross-project isolation, documenting the evidence contract.
- [x] 6.2 Build the follow-up UI with source navigation and explicit suggested scenario changes; browser-test question/answer/citation navigation, provider failure and no silent project mutation.
- [x] 6.3 Persist result-linked feedback and review status; test exact assessment/constraint/source targeting, restart and operator retrieval, and document that user feedback cannot directly activate a rule or trusted fact.

## 7. Admin ingestion and review (S1, S3, S7, B6)

- [x] 7.1 Add an operator access boundary and APIs for real source acquisition, extraction, inspection and review events; test unauthorized mutation rejection, stale-source rejection and attribution, documenting local configuration and production identity requirements.
- [x] 7.2 Build source/candidate/current comparison with validation failures, page/passages, corrections and reject/review/activate controls; browser-test the actual pipeline and assert no simulation or direct unvalidated activation.
- [x] 7.3 Connect feedback triage and eligible rollback/history to review; test a disputed result through an attributed corrected version and verify historical assessment reproduction and current-source eligibility checks.

## 8. Full PRD release (all IDs)

- [x] 8.1 Run the frozen holdout suite from an empty generated-observation cache without per-address edits; record all attempts, accepted field accuracy and extraction time, achieve five of six legible holdout maps with usable dimensions and zero accepted identity/unit errors, and leave this task open if the gate fails.
- [x] 8.2 Run all three project selections across the real cohort and verify at least two meaningful positive scenarios per package plus exceptions against independently derived expectations; link each result to source/model/review evidence and distinguish agent checks from independent professional validation.
- [x] 8.3 Measure end-to-end responsiveness, automatic-fact coverage and user effort; verify initial context ≤30 seconds under stalls, loaded p95 <1 second and bounded visible document jobs, reporting actual cold-extraction p95 against the 120-second target and any missed gate.
- [x] 8.4 Exercise the complete user journey including scenario comparison, feedback, grounded follow-up, map linkage, geometry export and admin correction/activation; inspect desktop/mobile captures and verify persistence/recovery on restart and source/model failure.
- [x] 8.5 Update the actionable production architecture and runbook for the implemented full-feature POC, including AWS-oriented UI/API/worker/PostGIS/object-store/identity/monitoring/restore boundaries; verify every diagram component is labeled implemented or proposed and fresh-checkout commands work.
- [x] 8.6 Run all backend/browser/build/OpenSpec checks and produce a PRD matrix with evidence links, pass/partial/fail per row, actual effort versus the original week and remaining risks; do not declare full PRD delivery unless every agreed release gate is met.

## Workflow follow-up

- Reconcile/synchronize the two completed component changes without losing their added requirements, then synchronize this change after acceptance.
- Archive only after reviewing the complete release report. Keep independent professional validation and actual production deployment clearly separate from the delivered POC.
