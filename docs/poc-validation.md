# Current POC validation and demonstration

This report supersedes the unconditional completion labels in the earlier release report. It separates implemented features, observed usefulness and unresolved facts. External reviewers are not a delivery dependency.

## Reproducible checks

- `PYTHONPATH=. .venv/bin/python scripts/validate_poc.py` runs current rules over16 retained real parcel contexts, all3 project types, with2 explicitly separated applicability modes:96 assessments. It does not fetch current GIS or claim the recorded snapshots are newly acquired.
- Backend tests cover source-backed expected rule calculations, recorded map reference readings, Stagg's179.55ft depth, applicability exclusions, source changes, malformed responses and cache invalidation.
- Browser tests cover the design conflict/save/restore flow, sourced guidance and overrides, mobile, evidence, source failure/retry and scenario isolation.
- `node frontend/scripts/poc-live.mjs` performs a real Kittyhawk lookup, waits for the public-map reader, saves a scenario and asks about its recorded depth through the configured subscription model. It writes live evidence and screenshots.
- `node frontend/scripts/poc-demo.mjs` opens the saved Stagg project, changes19ft to15ft, saves an alternative, checks mobile, then injects one HTTP503 search failure and retries against the real service. The503 is deliberately simulated, not a claimed upstream outage.

## Observed outcomes

Current replay, source facts plus design choices only:

| Package | Evaluated | Partial |
|---|---:|---:|
| Single-family |0|16|
| ADU |6|10|
| Guest house |0|16|

The hypothetical-applicability mode is separately retained in `data/delivery/poc-polish/cohort.json`; assertions are not verified facts. Partial does not mean every constraint failed. Inspect each row's values and blockers. No partial result is counted as a fully evaluated assessment.

Six frozen map reference cases were checked. Accepted readings had no discrepancies against those recorded references; one case still lacks expected depth/area and the irregular case has no accepted scalar dimensions. The separate Stagg reference retains179.55ft derived depth. This is bounded source/reference verification, not universal extraction accuracy.

Live7137Kittyhawk: initial structured results10.653s; map completion50.148s; completed-job reuse133ms. A separate real fresh acquisition changed the retrieval timestamp but retained identical document content and reused the same completed job; latest source refresh took9.721s. These are single-run observations, not p95 estimates or a claim that cold lookup is instant.

The real follow-up correctly accessed the125ft map reading, its source assumptions and unresolved assessment/geometry facts through citeable evidence IDs. Original answers and screenshots are retained. Stagg's19ft proposal visibly exceeded16ft; a15ft alternative was saved with immutable evidence and questions re-enabled only after save. Mobile layout had no horizontal overflow. Controlled503 recovery returned a real candidate after retry.

## Implemented improvements

Map-reading reuse ignores acquisition timestamps within a UTC day but includes parcel identity, map bytes, geometry, jurisdiction/regime, prompt, derivation version and guidance hashes. A changed validation context cannot attach an older reading. Supplemental sources can remain reused through the rest of that UTC day; the following day permits rereading.

Input guidance distinguishes automatically established source facts from design choices and research checks, explains required evidence and preserves explicit overrides. A negative coastal screen no longer overrides a user-reported coastal conflict. Bedrooms/stories are explicitly contextual-only. Unknown ordinary-lot, neighbor, approval and design exceptions remain unresolved rather than being fabricated.

Follow-up evidence includes saved parcel facts, readings, uncertainties, source status and geometry limitations, in addition to rule citations and design inputs. It excludes raw GIS feature arrays and retains source isolation and exact-quote validation.

## Demonstration sequence

1. Search7137Kittyhawk. Explain that initial facts arrive before map extraction; unresolved zoning remains visible.
2. Inspect its125ft reading, original source and uncertainty. Save and ask what depth is established.
3. Open Stagg and select the19ft design. Use **Edit proposed height**, enter15ft, inspect the changed result and save a named alternative.
4. Compare proposed quantities against limits and inspect source evidence. Show that unsaved edits disable questions about an old revision.
5. Demonstrate controlled source failure and successful retry, explicitly labeling the injected failure.

## Remaining boundaries

Cold extraction still takes tens of seconds. Main-building and guest-house applicability often needs facts not established by current public sources. Regulatory coverage and geometry remain intentionally bounded; source dates and failed publisher refreshes remain visible. The one-week historical timebox remains unverified. These limitations qualify outcomes, not whether the listed UI/engine features exist.
