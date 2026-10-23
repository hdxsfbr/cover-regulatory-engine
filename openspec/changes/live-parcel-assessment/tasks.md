# Tasks

Prerequisite: synchronize/archive the completed `initial-parcel-assessment` using its workflow before applying this change; verify its three capability specs exist as the baseline. Planning this change does not archive or alter the prior change.

## 1. Diagnostic reasons

- [x] 1.1 Add stable source/spatial diagnostics while retaining existing fields; verify tests distinguish recorded 2202010006 source failure, Rhea Court positive sliver matches, coverage gaps, no-match, not-checked and invalid geometry without inventing conflicts.
- [x] 1.2 Render source-linked diagnostic explanations in context/results and document the additive response fields in docs/api.md; verify browser text and API examples match the actual failure cause.

## 2. Fresh context and snapshot integrity

- [x] 2.1 Expose the fresh context option, bypass and evict the selected parcel's previous cache entry on explicit refresh, and retain bounded source handling; verify cached-success-to-failure and failure-to-success adapter/API tests with old snapshots unchanged and no fixture fallback.
- [x] 2.2 Document and test refresh semantics, retrieval provenance, successful cache replacement and 25-second overall timeout; verify incomplete retry results cannot masquerade as previous current success and completed independent sources survive.

## 3. Mode and project state

- [x] 3.1 Show persistent live/recorded labels and accurate replay controls; update README/demo instructions and verify live startup plus recorded replay in browser tests without silently switching the configured mode.
- [x] 3.2 Separate parcel selection from same-parcel refresh and retain selected AIN on early failure; verify dimensions, project type and note survive refresh/expiry recovery while selecting a different parcel clears parcel-specific entries.
- [x] 3.3 Compare applicability evidence across snapshots and clear assertions on substantive changes or unavailable evidence; verify timestamps/order-only changes preserve checks, geometry/status/overlay changes clear them, and new results reference the replacement snapshot.
- [x] 3.4 Make failed-source rows accurately offer whole-context refresh, provide early-failure and expiry recovery, and protect pending results with existing cancellation/generation guards; verify keyboard operation, failed retry, late context and late assessment responses in browser tests and document the behavior.

## 4. Integrated acceptance

- [x] 4.1 Run backend tests, TypeScript/production build and browser acceptance together; verify all source-recovery scenarios and existing R1-1, ADU, guest-house, Chapter 1A and ambiguity regressions, with every scenario mapped to evidence.
- [x] 4.2 Record separate live smoke observations for 7537 Louise and one supported cohort parcel, including elapsed time and per-source statuses; verify bounded truthful failure or recovery without claiming guaranteed upstream success, and update acceptance evidence and roadmap status.

## 5. Empty proxy response regression

- [x] 5.1 Handle empty/non-JSON API responses in the shared client, preserve structured API errors, and verify browser regression tests, production build and a restarted live API through the frontend proxy.

## 6. Interactive lookup performance

- [x] 6.1 Add a compatible compact context response for the browser while retaining complete server evidence, improve loading feedback, and verify payload reduction, API equivalence, browser recovery tests and live timing.

## 7. Visible loading feedback

- [x] 7.1 Add immediate accessible spinner feedback to search, selected parcel and refresh controls; verify pending/success/failure transitions, reduced-motion behavior and production build.

## Workflow follow-up

- Review and archive this change after tracked acceptance is complete.
- Propose `applicability-evidence` using the discovery and exit criteria in `openspec/roadmap.md`; later phases are not implied complete by this change.
