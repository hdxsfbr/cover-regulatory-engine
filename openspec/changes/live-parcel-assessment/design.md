# Design

## Context

See proposal.md for the problem. `backend/app.py` already defaults to live mode unless `COVER_FIXTURE_MODE=1`; the demonstrated process was deliberately launched in recorded mode. `backend/gis.py` already has 22-second request and 25-second overall context budgets, per-source provenance and a 15-minute successful-context cache. `context_for` accepts `use_cache`, but the HTTP endpoint does not expose a fresh request.

The summarizer currently collapses unavailable zoning, overlap and gaps into one message. Frontend refresh/source-retry buttons call parcel selection, which clears inputs and reuses the normal cache. Recovery controls rely on returned parcel attributes, making early parcel failure awkward. Existing tests cover fixture flows and stale parcel responses, but not a successful cached result followed by fresh failure or assertion invalidation.

The completed initial change was synchronized and archived on 2026-10-22. Its three main specs are the baseline for this additive change. The program beyond this change is tracked in `openspec/roadmap.md`.

## Goals / Non-Goals

**Goals:** Explain failure accurately, permit real fresh reads, and maintain a consistent parcel/project/snapshot relationship through retries using existing modules.

**Non-Goals:** Per-layer snapshot merging, automatic polling, new GIS sources, automated legal interpretation, rule expansion or shared persistent state.

## Decisions

### 1. Keep mode server-owned

Reuse `/api/config` and result `mode`; display a persistent label and a recorded-mode explanation. README presents live startup first and recorded demo separately. Recorded controls say replay, not retry live sources. Do not add a browser switch that can disagree with backend mode or mix live and recorded records. A future runtime mode switch is unnecessary for this change.

### 2. Add backward-compatible diagnostics

Keep `issues` and existing status fields. Add a diagnostics array with `code`, `message`, relevant source names and retryability. Use distinct codes for source unavailable/not checked, invalid geometry, zoning no-match, incomplete coverage and multiple positive matches. Allow more than one reason when supported by returned evidence; do not infer a coverage gap from a missing layer alone. Preserve all spatial matches and existing conservative evaluation gates. Update summarization tests to assert reasons, not only status.

### 3. Whole-context fresh refresh

Add `fresh: bool = false` to `GET /api/parcels/{ain}/context`; in live mode call `context_for(..., use_cache=not fresh)`. Each result gets a new server-owned UUID as today. Existing snapshots are never mutated. Explicit fresh attempts evict the selected parcel's old successful cache entry before querying; otherwise a later normal lookup could reintroduce a success that the fresh attempt could not confirm. Cache only fully successful new results. Keep current request/body/overall budgets and no automatic retries.

Source-specific failure rows offer “Refresh parcel sources” rather than implying only that source is retried. Whole-context refresh avoids combining records from different parcel geometry versions and requires less code than per-layer merging. Previously completed evidence can stay visible while loading only if labeled previous and its assessment is pending; the new response replaces context as a whole. On transport failure without a response, keep the previous snapshot explicitly labeled previous, with no current assessment.

### 4. Separate selection from refresh

Track selected AIN independently of returned attributes so refresh works even when the parcel service fails. A new parcel clears dimensions, checks, note and assessment; same-parcel refresh retains dimensions, project type and note. Reuse generation guards and cancellation for context and assessment requests. Expiry recovery calls the same fresh path.

Preserve applicability checks only if a deterministic comparison shows equivalent evidence: jurisdiction, zoning status and complete matches, parcel geometry, and selected-overlay statuses/features. Compute an opaque fingerprint server-side from these records and return it with context, or null when comparison is unsafe. Exclude retrieval timestamps and cache origin from comparison; ignore feature ordering via stable serialization/sorting. Any substantive difference, unavailable/invalid evidence, or inability to compare clears all applicability checks with an explanation. Preserve the dimension note as user-supplied history, not fresh verification. Clearing all checks is intentionally conservative and avoids a new predicate-dependency framework.

### 5. Acceptance without upstream flakiness

Use recorded 2202010006 for the missing-zoning explanation and 2126037055 for genuine sliver ambiguity. Mock transport sequences through the real backend to test unavailable-to-success and cached-success-to-failure, with clearly labeled synthesized recovery data if no actual new recording is available. Browser tests cover preserved entries, cleared assertions, expiry, failed parcel lookup and overlapping requests. Keep ADU/guest-house regression checks.

Record a separate live smoke check for 7537 Louise and a supported cohort parcel, including timestamps and all source states. Upstream success is an observation, not a CI requirement or SLA; a failure must still satisfy bounded truthful behavior. No fixture is relabeled as a live successful lookup.

## Risks / Trade-offs

- More upstream requests on explicit refresh → one request batch per user action, bounded deadline and no automatic loop.
- Legitimate evidence changes invalidate assertions → preserve dimensions and explain exactly why checks require review.
- Equality comparison misses or overreacts to changes → compare only applicability-relevant records, canonicalize ordering, and test both timestamp-only and geometry/status changes.
- Live sources remain intermittent → distinguish transport availability from legal applicability and retain explicit uncertainty.
- Older clients ignore new diagnostics → retain existing response fields; the new fresh parameter defaults to current behavior.

## Migration Plan

Synchronize/archive the completed initial change, then apply this additive change. No stored-data migration is required. Verify API and browser paths in both configured modes, record a bounded live smoke check, and update run/demo docs. Rollback restores the previous application code; source/rule snapshots remain untouched. This change does not deploy or change the running demo during planning.
