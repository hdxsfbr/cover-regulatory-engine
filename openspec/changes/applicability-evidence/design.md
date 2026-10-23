# Design

## Context

See proposal.md and audit.md. `gis.summarize` never emits `verified_facts`; `rules.assess` accepts only trusted context facts or manually supplied values/checks. A single free-text note currently attributes all user facts. The frontend hides reasons in details and presents five empty cards even after successful source retrieval. The existing snapshot, cache and fingerprint behavior is already implemented by live-parcel-assessment and must be preserved.

## Goals / Non-Goals

**Goals:** Connect inspectable public evidence to rule inputs, reduce repeated entry, and expose the exact remaining decision on every blocked card. Make source quality explicit without requiring a new database or model invocation per search.

**Non-goals:** Automatic legal interpretation of every scan, inventing proposed design inputs, treating an assessor lot as conclusive legal entitlement, or relaxing the five reviewed rules to manufacture numeric results. Operator map reading is distinct from independent legal review.

## Decisions

1. **Use parcel-provided map identity, not guessed address matches.** Validate `Assr_Map` as a book/page identifier and construct the approved County PDF resource URL. Store successful bytes under a content hash with source URL, retrieval time and visible map date where identified. Enforce PDF/content, size (10 MB), approved redirect hosts and bounded request handling. Document work must fit the existing 25-second source budget; time exhaustion produces an explicit unavailable document state. References can remain visible even when retrieval fails. This avoids unbounded arbitrary URL fetching and avoids assuming a whole map sheet is one parcel.

2. **Separate document observation from legal input acceptance.** A local evidence record contains AIN, tract/lot, fact key, value/unit, document hash and page/location, method, reviewer/time and exact review scope. Review confirms a transcription unless it explicitly establishes a legal interpretation with supporting evidence. Derived area references its width/depth dependencies. Reuse the local hashed-source and attributed-review pattern in backend/ingest.py, with a small parcel-evidence command/module rather than a generic document platform. Bootstrap reviewed observations for Lots 108 and 111 on the inspected sheet; use the same mechanism for any other parcel. Do not hardcode Louise values in the evaluator. For other scans, display the direct document and `needs-document-review`; do not claim universal OCR. Geometry estimates remain estimates, never a substitute for documented dimensions.

3. **Use explicit acceptance with retained source provenance.** Extend the assessment request additively with selected server-owned observation IDs. Validate IDs against the immutable parcel snapshot, current document hash and fact bounds. Resolve accepted values on the server; never trust client-provided review metadata. User acceptance for legal use is an assertion with medium confidence, separate from the operator's transcription review. Allow explicit numeric overrides, label them user supplied and retain their stated basis; conflicts require an explicit choice rather than silently preferring a source. Preserve legacy numeric/check/note clients. No new public endpoint can create trusted review records.

4. **Screen exact named layers, not a blanket restriction checklist.** Query Special_Areas/6 (Hillside Ordinance) and zma/zimas/1605 (Coastal Commission Permit Area), retaining raw response and query geometry. Use polygon intersection and known CRS; retain boundary ambiguity, incomplete-page and malformed-geometry handling. These named layers are observations, not replacements for `outside_hillside_coastal`. Their inspected metadata lacks sufficient statutory coverage documentation, so this change does not automatically promote their negative results. Display the no-match evidence as support for a targeted review. CPD Building Lines is a polyline layer and is only a research reference in this change; the current polygon helper must not be reused on it. Do not silently add a third incompletely researched screening layer.

5. **Return structured blockers from the evaluator.** Preserve existing reasons for compatibility; add stable blocker code, affected fact/check, explanation, evidence references and action kind/target. Action kinds cover source retry, observation review, project input, applicability review and unsupported scope. Prefer unsupported scope over an irrelevant missing-input task. Show a primary blocker and count/list of the remainder directly on the card. Use existing controls with stable IDs and focus behavior; keep long legal quotations in details. Link common blockers to one shared evidence panel to avoid five duplicated checklists.

6. **Include new evidence in refresh semantics.** Document content hashes, observation revisions and screening outcomes participate in applicability comparison. Store immutable full evidence server-side while compact browser context contains summaries/references. Unknown or changed source clears dependent acceptance; preserve typed dimensions and notes as user inputs pending review. No live call falls back to recorded documents. Unchanged evidence can retain acceptance under the existing cache/refresh rules.

7. **Test the whole path, not a positive evaluator shortcut.** The existing five new manual numeric fields and five checkboxes are the baseline. Two Louise cases must reduce three dimension transcriptions to zero through reviewed observations, though legal-use acceptance and design/applicability input remain explicit. Measure counts separately; do not describe confirmation clicks as eliminated review. Exercise source failure and source change, irregular Lot 107, Rhea and Beverly Hills. Use retained source bytes to derive expected dimensions outside the evaluator. Test hypothetical project choices as hypothetical, and do not mark independent project validation complete.

## Risks / Trade-offs

- Scanned maps and ditto marks resist reliable generic extraction → reviewed observations with page/lot locations; no unreviewed auto-promotion. This supports a growing reviewed corpus, not instant extraction for arbitrary properties.
- Assessor sheet stamped 1985 may not reflect later recorded changes → show document vintage, distinguish transcription from legal applicability, invalidate on changed/conflicting evidence; don't label current retrieval as current survey.
- Named GIS no-match can be overread as statutory absence → display exact layer and coverage limitation; leave legal predicate unresolved without documented support.
- More network work can undo the latency fixes → enforce one total context deadline, bound bytes, cache unchanged documents, keep immediate loading and partial outcomes.
- An actionable blocker can still mask a useless product → require zero dimension transcription on both supported cases, measured remaining work, and actual browser walkthroughs before completion.

## Migration Plan

Add new evidence and API fields without removing existing request/response fields. Extend recorded fixtures separately from immutable historical failure fixtures. Validate current rules unchanged. Run isolated backend/browser suites without replacing the user's running live service, then restart only the updated backend and inspect the user-facing flow. Rollback removes new evidence use/UI fields while preserving stored documents and the prior numeric-input path. Archive/sync the prior live change in its normal workflow without overwriting its delta requirements; the new deltas add requirements under the existing capability names.
