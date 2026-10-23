# Regulatory engine delivery roadmap

## Objective and current position

Deliver real parcel assessments with traceable answers and progressively less manual input, then expand supported projects and prepare production operations. This extends beyond the original one-week proof of concept; it is a phased program, not a one-week delivery promise.

`initial-parcel-assessment` has 28 completed implementation tasks and passing acceptance evidence, and was synchronized/archived on 2026-10-22. It already implements live GIS, a separate recorded demo, five narrow R1-1 scalar calculations and an operator extraction/review pipeline. Its positive design examples use hypothetical dimensions/assertions; they are not independent real-project validations or professional zoning approvals.

Each phase uses OpenSpec proposal → specs/design/tasks → apply → acceptance review → sync/archive. Phase 1 is implemented and acceptance-tested, awaiting review/archive. Later entries are explicit backlog scope and completion gates; create their full change artifacts after the preceding evidence resolves scope. Do not mark a milestone complete merely because code exists or an LLM agrees with it.

## Sequence

| Phase / planned change | Depends on | Deliverable | Completion gate | Status |
| --- | --- | --- | --- | --- |
| 0. Close initial change | Completed acceptance | Baseline main specs and archived initial change | Archive/sync verified with no outstanding task loss | Complete — archived 2026-10-22 |
| 1. `live-parcel-assessment` | 0 | Clear mode, specific diagnostics, fresh bounded retry and consistent project state | Recovery tests plus separate live observations; no hidden fixture fallback | Complete implementation — review/archive next |
| 2. `applicability-evidence` | 1 | More automatically sourced applicability facts and per-fact evidence/missing-data controls | Source-backed positive, negative, unknown and conflict cases; manual workload measured | Implemented — 13/13 tasks; see `docs/applicability-acceptance.md`; review/archive pending |
| 3. `real-project-validation` | 2 | Independently reviewed real-project comparison corpus and discrepancy report | Reviewed expected answers, reproducible runs and resolved discrepancies within declared scope | Backlog; independent project evidence required |
| 4. `adu-assessment` | 3 | Explicitly bounded LA City ADU rules and supported/excluded cases | Current official dependencies reviewed, independent positive/exception tests pass | Backlog; legal/source research required |
| 5. Coverage expansion series | 4 | Guest-house rules, named additional zoning designations and restrictions | Each separate change passes its own source/applicability and regression gates | Backlog; select precise scope per change |
| 6. Production delivery series | Proven representative coverage from 3 onward | Durable evidence, monitoring/review operations and deployed service | Reproducibility, source-change withholding, restore/recovery and deployment smoke checks | Backlog; environment/operational decisions required |

The default order is sequential. Storage work can move earlier if the real-project corpus outgrows local artifacts, but it requires an explicit revised OpenSpec change rather than silently replacing the small prototype architecture.

## Phase 1 — Reliable live assessment

See `changes/live-parcel-assessment/`. Build on existing live adapters. Correct the generic zoning warning seen for 7537 Louise, make fresh reads actually bypass cache, distinguish recorded replay, and preserve user work through retry. Keep all current regulatory exclusions. Exit with a working live evidence workflow, not a promise that every upstream service always responds or every parcel can be evaluated.

## Phase 2 — Less manual verification

The `applicability-evidence` change has 13/13 implemented tasks, 59 passing backend tests and 18 passing browser tests. Acceptance is documented in `docs/applicability-acceptance.md`. Its audit records five live parcel runs, the browser blank-card behavior, an inspected public assessor sheet and two named screening-source probes. The selected change adds reusable reviewed document measurements and visible actionable blockers; it does not assume generic scan interpretation or promote GIS no-match into legal clearance. See `changes/applicability-evidence/audit.md` for evidence and limits.

First inspect official sources for the existing rule predicates: hillside/coastal status, applicable plans/approvals/building lines, frontage exceptions and project-specific roof/wall conditions. Document availability, authoritative meaning, geographic coverage, currency and access/reuse constraints for each. GIS evidence cannot establish design-specific wall lengths, roof pitch or legal survey dimensions by itself.

The proposal must name the exact facts it will automate based on that investigation. For each fact, retain value/units, source passage or feature, retrieval/version, spatial applicability and verification/reviewer status. Show missing evidence next to the affected constraint. Allow attributed per-fact manual evidence when automation cannot establish it; an entered URL or uploaded document is not automatic verification. Start with references/text using existing patterns; add file storage only if needed by the selected workflow.

Test conflict, unknown coverage, stale sources and invalid geometry as well as yes/no matches. Never infer absence from an incomplete dataset. Measure the number of manual facts required before and after for the representative cohort; do not promise to eliminate all manual verification. Exit with fewer demonstrably manual steps and no weaker applicability gates.

## Phase 3 — Independent real-project validation

Obtain permission to use a small representative corpus with actual project dimensions, dated plans/surveys and independent expected assessments. A suitable reviewer or attributable official project decision must supply the independent reference; a second model run is not a substitute. Begin with at least two real supported R1-1 projects plus excluded/ambiguous examples, keeping synthetic tests separately labeled.

Freeze the source edition and project evidence for each comparison. Compare each yard, height and floor-area result, its applicability gates and reasons; report disagreements and missing evidence rather than averaging them away. Reproduce results against the same facts/rules without live model access. Resolve discrepancies by correcting rules, inputs or explicit supported scope, with recorded review.

Before applying this phase, identify who supplies and reviews the project cases. If that evidence is unavailable, complete useful tooling and clearly leave the independent-validation gate unfinished. Never relabel the existing hypothetical examples as real-project validation.

## Phase 4 — ADU coverage

Research then-current official California and LA City requirements, their precedence, local implementation and relevant exceptions. This roadmap asserts no current legal dimensions or entitlement rules. Before proposing implementation, choose a precise supported ADU category based on complete source dependencies and obtainable test cases; enumerate excluded ADU variants and why. Do not reuse the ordinary R1 main-building rules as an ADU fallback.

Produce an ADU applicability matrix, reviewed versioned rules, required project facts and independent positive/boundary/exclusion cases. Extend the finite evaluator only where required and maintain source citations, confidence limits and unknown handling. Keep unsupported ADU variants explicit. Pass existing single-family regressions before changing the UI from unsupported for the newly supported category.

## Phase 5 — Additional coverage

Use separate changes for `guest-house-assessment`, `additional-residential-zones` and `additional-property-restrictions`, splitting further when distinct legal regimes require it. Select named zones and specific restriction layers from validated demand and available evidence before drafting executable tasks; “all zones” and “all overlays” are not acceptance criteria.

Distinguish guest houses from ADUs through source-backed project definitions. Preserve complete zone strings, prefixes/suffixes, special conditions and precedence. A positive overlay can continue to require review until its effect is modeled; adding a dataset does not mean its regulations have been implemented. Each change requires positive, negative, unknown and exception tests, independently checked expected results, and regression across all previously supported project types. Chapter 1A is a distinct future scope, never an implicit extension of Chapter 1.

## Phase 6 — Production preparation and delivery

Split into concrete changes when needed:

- **Durable evidence:** persist immutable source, fact, assessment and rule versions; retain original snapshots, provenance and review history. Use the responsibilities in `docs/architecture.md` to decide database/object storage based on actual workload. Verify restart persistence, rollback, backup/restore and historical reproduction.
- **Monitoring and review:** schedule source refresh checks, distinguish publisher failures from actual changes, invalidate affected current rules when dependencies change, and require attributed re-review. Deduplicate unchanged alerts and route actionable failures to an agreed operator. Verify changed-source, failed-fetch, reviewer-access and rollback cases.
- **Deployment:** specify intended users, hosting target, budget, access controls, data retention, secrets handling and operational ownership before provisioning. Build environment configuration, readiness checks and a reversible release path. Verify production smoke checks, concurrency/request limits, observability, restore and rollback. Preserve fixture/live separation; do not publicly expose project evidence without an appropriate access model.

Hosting/provider choices and ongoing operating costs are not decided by this roadmap. Deployment is a separate implementation change once those concrete requirements exist, not an action performed by this planning step.

## Milestone evidence

The “real assessment with minimal manual input” milestone is phases 1–3: live reproducible context, a measured reduction in required manual facts, and agreement with independent real-project evidence within a declared scope. Subsequent milestones add named supported project categories and production operations. None by itself establishes complete legal buildability, construction-code compliance or permit approval.
