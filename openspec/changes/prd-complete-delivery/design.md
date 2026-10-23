# Design

## Context

See docs/prd-delivery-plan.md for the audited PRD matrix and delivery gates. The implementation currently has four API routes, in-memory snapshots, local JSON sources, a generic GIS query layer, a five-operation R1-only evaluator, a formula-fed extraction CLI and two parcels' curated map observations. React contains lookup, map, cards and input controls in one application file. There is no persistent project/job store, chat, feedback, geometry generation or admin UI. Existing version/citation and refresh protections are useful and must remain.

Two completed changes have not been synchronized/archived. This change adds general behavior and replaces the main spec's blanket ADU/guest-house exclusion only for explicitly reviewed packages. Preserve the completed changes' evidence requirements during synchronization; do not lose them by copying an older main spec over their deltas.

## Goals / Non-Goals

**Goals:** Deliver the full PRD feature journey with measurable generalization, bounded regulatory coverage and all bonus features; connect real services rather than mock endpoints; allow reuse across properties and eventual jurisdictions.

**Non-goals:** Every zoning regime, every accessory-unit variant, legal sign-off, full construction-code compliance or a production deployment. These are distinct from the general input/evidence workflow. Mocks remain explicitly labeled test/demo evidence, never the live behavior.

## Decisions

1. **Use one integrated release contract with vertical implementation slices.** Keep the PRD matrix and release gates independent of OpenSpec task progress. Twelve real parcels and six frozen non-Louise holdouts guard against the previous curated-example failure. Do not make independent professional validation a prerequisite for all further feature work; retain it as a separately labeled production-readiness activity. This replaces the old serial roadmap that deferred named building types and every bonus indefinitely.

2. **Persist the POC with SQLite plus content-addressed files.** Use standard-library SQLite for projects, scenarios, jobs, references, review events and feedback. Keep original document bytes and rule/source versions in the existing hashed artifact layout. Transactions/atomic writes and a minimal versioned migration preserve user work. A bounded local worker with durable job state performs document/LLM acquisition; initial UI polling avoids introducing streaming infrastructure before it is needed. Production migration to PostGIS/object storage/queue remains explicit in the architecture.

3. **Make extraction generic but evidence-tiered.** Acquisition uses structured parcel identities and approved source references. Rendering/text/OCR/vision yields candidate observations with source regions; model output cannot choose unrestricted URLs or assert legal verification. Validate identity, units, value ranges, arithmetic, geometry and frontage evidence. Store distinct extracted, corroborated, reviewed, user-assumed and conflicted states with reasons. Reuse the existing review path for difficult cases, but do not require prewritten review records before the first attempt for a new parcel. Preflight document/model capability and latency before selecting any new dependency; prefer available renderer and current subscription adapter.

4. **Turn rule fragments into the source of evaluator operands.** Keep a finite typed expression interpreter. Generalize expressions/predicates only for the reviewed packages, with units, jurisdiction, regime, project type, dates, priorities and referenced exceptions. Remove prompts that prescribe the answer; use changed-source tests to demonstrate extraction independence. An LLM proposes structured candidates, never executable Python. Cross-reference and precedence decisions are reviewed data, not an unrestricted inference at every request.

5. **Split observed facts from legal interpretations.** Each fact and decision has explicit dependencies and source-quality status. Replace broad checkbox gates with individual facts and targeted design questions. Computable facts are supplied automatically; uncertain legal branches can produce separately labeled conditional results with declared assumptions. This preserves unconditional safety while providing useful synthesis instead of five blank cards. Model confidence is not a permit probability.

6. **Package three project definitions independently.** Preserve the reviewed single-family subset; research and implement one detached ADU and one detached guest-house branch with explicit eligibility and exclusions. Do not select numerical thresholds in this planning step. The task is to establish them from current primary sources, resolve dependencies, validate and activate them; always-unsupported output is a failed task, not an alternative implementation. Record missing official dependencies as blockers if encountered.

7. **Extend the existing UI around a project revision.** API routes add project/scenario CRUD, evidence jobs, feedback, grounded questions and controlled review operations. Keep backward compatibility for current lookup/assessment routes during migration. Split frontend components only where new surfaces need it: project controls, evidence viewer, assessment summary/cards, map, follow-up and review. Every request carries project/revision identity. Map and card selection share constraint IDs. Avoid adding a global state framework without demonstrated need.

8. **Generate geometry only from supported edge semantics.** Use Shapely in an appropriate projected CRS with classified front/rear/side edges and per-edge setback operations. Verify edge roles from parcel/record/street evidence; unknown classifications remain explicit. Handle holes, corners, empty and multipart results. Export labeled GeoJSON with source/rule/project versions and conditional status. Existing footprints remain contextual; the envelope is not a construction-ready site plan.

9. **Ground chat and isolate review actions.** Follow-up retrieves from the selected immutable assessment and supporting source subset, references evidence IDs and cannot mutate project state silently. Feedback is append-only input to review. Operator endpoints require a local configured credential/access boundary; ordinary browsers cannot activate rules. Source text and model output never grant authority. The POC remains local by default; production identity and model-provider arrangements are documented separately.

10. **Preserve model authorization.** Continue subscription-only Claude use with sanitized environment and auth verification. Prove image/document invocation and deterministic result parsing in a Day-1 probe. Do not use API credits, impersonate a hosted subscription API, or silently replace the provider. If the supported invocation cannot handle the selected document workflow, report the concrete constraint before any paid fallback. Core already-reviewed calculations remain available during model failure.

## Risks / Trade-offs

- Heterogeneous maps can defeat automatic lot/dimension interpretation → frozen legible holdout accuracy gate, source crops, deterministic checks, explicit ambiguous cases; never seed around a failed holdout.
- Statutory and local dependencies can exceed a one-week effort → bounded project packages, early official-source review and explicit blockers; no invented thresholds or hidden exceptions.
- Full-feature scope versus original one-week POC → five-day target with Day-1 feasibility gates; current forecast 10–15 focused days is an estimate and does not waive the timebox. Report schedule failure rather than claiming complete compliance.
- Local model jobs can be slow/unavailable → separate acquisition from subsecond loaded evaluation, explicit job deadlines and progress, cancellation and content-hash reuse; no unbounded spinner.
- Saved scenarios can look current after source changes → immutable historical versions plus explicit current pointers/reassessment; tests cover source mutation and restart.
- More features can obscure evidence → one project summary, targeted questions, shared source viewer and linked map/cards; inspect the actual desktop/mobile flow, not just API outputs.

## Migration Plan

1. Freeze existing passing regression evidence, record actual gaps, and retain the original failure fixtures.
2. Add the local store/schema with import for existing source/review artifacts; never relabel existing Codex review as professional verification.
3. Introduce optional job/project routes while keeping current lookup clients working. Move new extraction through the general path; the Louise records remain test/reference data.
4. Add and review rule packages behind explicit coverage metadata; update the blanket unsupported gate only as each package becomes evaluable.
5. Wire workspace/geometry/chat/review interfaces and run release gates on an empty generated-observation cache.
6. Preserve old versions and back up local state before migration. Rollback restores the prior schema/data snapshot and prior active rule pointer; failed extraction never mutates historical assessments.
7. Reconcile and synchronize pending OpenSpec deltas in dependency order after acceptance. Deliver local run/demo instructions and a clearly proposed production architecture, without provisioning cloud services as part of planning.
