# Tasks

## 1. Public parcel documents

- [x] 1.1 Add validated assessor-map discovery and bounded retrieval with hashes/provenance to parcel context; verify valid/missing references, HTTP failure, invalid PDF, excessive bytes, redirect allowlist and total lookup deadline with focused tests, and document the context fields in docs/api.md.
- [x] 1.2 Add a reusable local document-observation and attributed review path; verify identity/page/hash/units validation, rejection of ambiguous and unreviewed observations, and reproducible review commands documented in the evidence workflow.
- [x] 1.3 Inspect and register width/depth observations for Tract 16180 Lots 108 and 111 from the retained public sheet, with separately derived area and transcription-only review scope; verify both load through the generic path and that irregular Lot 107 does not inherit their dimensions. Preserve source bytes and provenance in the appropriate implementation data directory.

## 2. Applicability observations and evidence lifecycle

- [x] 2.1 Integrate the two named hillside/coastal screening sources with independent status/provenance and source-specific limits; verify positive, negative, unavailable, truncated and invalid-geometry cases, document their coverage limits, and assert no negative query automatically clears the legal predicate.
- [x] 2.2 Include document hashes, observation revisions and screening state in immutable snapshots and applicability comparison; verify unchanged evidence preserves acceptance, changed/conflicting/unavailable evidence invalidates it, recorded mode stays offline, and compact responses preserve evidence references. Document refresh semantics.

## 3. Assessment contract and provenance

- [x] 3.1 Accept server-owned observation references as attributed user selections while retaining numeric overrides and legacy request fields; verify parcel/hash binding, stale/conflict rejection, numeric bounds, client verification-spoof rejection and unchanged scope/confidence gates. Document the additive API contract and acceptance-versus-verification distinction.
- [x] 3.2 Produce structured category-specific blockers with action targets while retaining legacy reasons; verify missing dimensions, proposed height/roof inputs, legal checks, source failure, no reviewed rule, conflict and unsupported scope receive the right action without numeric leakage.

## 4. User-facing completion path

- [x] 4.1 Add parcel document and screening evidence panels with exact source links, identity, vintage, observations and explicit dimension acceptance; verify both Louise cases require zero dimension transcription and that keyboard users can inspect and accept evidence with provenance retained.
- [x] 4.2 Show the primary blocker and remaining blockers directly on cards, with actions focusing the appropriate evidence/input control; verify unsupported projects avoid misleading data-entry prompts, loading/retry feedback remains immediate, and documented frontend behavior matches screenshots at desktop and mobile widths.
- [x] 4.3 Preserve inputs/notes and invalidate dependent acceptance through refresh, source changes, failures and parcel switching; verify delayed old requests cannot restore stale evidence or numbers using browser regression tests.

## 5. Integrated acceptance

- [x] 5.1 Run the source-backed recorded cohort for both Louise supported cases, Lot 107, Rhea, outside-city, Chapter 1A, positive overlay and unavailable sources; include single-family, ADU and guest-house selections. Verify expected arithmetic independently from retained source passages, labeling proposed designs and unresolved assertions explicitly rather than claiming independent legal validation.
- [x] 5.2 Walk the actual running UI from lookup to evidence acceptance and project input for both Louise parcels, plus ambiguity and failure paths; inspect screenshots, record before/after transcription/check counts and latency, and confirm every constraint has a traceable answer or visible actionable blocker in docs/applicability-acceptance.md.
- [x] 5.3 Run backend and isolated browser regressions, production build and strict OpenSpec validation; document actual results and update roadmap status without marking the real-project-validation phase complete. Leave any failed acceptance task unchecked rather than narrowing the completion criterion.

## Workflow follow-up

- Synchronize/archive the completed live-parcel-assessment change through its existing workflow, preserving its requirements.
- Review this change's acceptance evidence before synchronizing/archiving it. Independent real-project validation remains the next separate phase.
