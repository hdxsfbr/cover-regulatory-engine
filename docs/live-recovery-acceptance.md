# Live parcel recovery acceptance

This change adds source recovery without expanding regulatory coverage. The initial change is archived at `openspec/changes/archive/2026-10-22-initial-parcel-assessment/`; its three main specs were synchronized and validated before implementation.

## Behavioral evidence

| Scenario | Evidence |
| --- | --- |
| Recorded failure is a replay, not a new live finding | Browser recorded-failure test uses real saved 2202010006; API fixture-fresh test prohibits upstream calls |
| Missing zoning evidence differs from conflict | Backend recorded reasons test asserts unavailable without overlap/gap claims; browser checks source-linked diagnosis |
| True spatial ambiguity remains | Rhea Court and gap fixture tests retain intersections and specific diagnostics; existing single-family/Chapter 1A regressions |
| Fresh read bypasses cache, failed read cannot restore previous success | Adapter/API sequence exercises cached success, fresh failure, normal failed retry and fresh recovery; old server snapshots remain unchanged |
| Overlapping older success cannot repopulate cache | Async older-success/newer-failure test; only latest in-flight lookup can write the selected parcel's cache |
| Same evidence preserves assertions | Backend fingerprint tests ignore retrieval metadata and feature ordering; browser replay retains checkboxes, dimensions, note and project type |
| Changed evidence clears assertions | Backend tests vary geometry, layer status and overlay features; browser changed-evidence test confirms reset, retained dimensions and replacement snapshot ID |
| Transport failure preserves prior evidence only as reference | Browser test checks previous-evidence label, no current assessment, no reevaluation on edit, and successful later recovery |
| Early parcel failure remains recoverable | Browser synthetic live response omits parcel attributes and keeps selected AIN; whole-context refresh succeeds |
| Expired snapshot recovers without losing inputs | Browser injects 410, then verifies fresh-context recovery with dimensions retained |
| Late context or assessment cannot overwrite current state | Browser delayed refresh/new parcel and delayed ADU assessment tests |
| Slow upstream response remains bounded and partial | Real 25-second outer-budget test stalls one transport for 60 seconds, requires completion below 30 seconds and retains parcel/overlay successes |
| Unsupported projects stay unsupported | Existing ADU/guest-house/Chapter 1A tests plus refresh with both unsupported project types |

Browser synthetic live-mode responses are labeled as test injections in their source; they are not live GIS validation. Browser tests block external network requests. The distinct live smoke observations below use official endpoints and preserve per-source provenance.

## Run and review

From README installation, run `uv run pytest -q`, `npm --prefix frontend run build`, and `npm --prefix frontend test`. Browser tests own their backend port while running. Start the normal backend without `COVER_FIXTURE_MODE=1` for live queries; recorded mode remains separately available for reproducible failure demonstrations.

The server returns opaque applicability fingerprints for comparison only, never as legal verification. Refreshing a parcel does not verify user-entered dimensions or establish unqueried site restrictions. The UI lists each unavailable source and offers whole-context refresh. Recorded-mode controls explicitly replay the existing evidence instead.

## Final results

43 backend tests pass, including the measured 25-second stalled-source budget; 11 browser tests pass; TypeScript and production build pass. The existing TestClient dependency emits one deprecation notice. OpenSpec main specs and the active change validate strictly.

Separate live observations are retained in `data/live-recovery-smoke.json`: APN 2202010006 (7537 Louise) resolved to R1-1 in 10.63 seconds and APN 2202010009 (7523 Louise) resolved to R1-1 in 9.61 seconds. All eight sources completed for each parcel. These observations demonstrate recovery from the old recorded timeout, not guaranteed future service availability or complete regulatory applicability. The recorded failure fixture remains intact for regression testing.

## Empty proxy response regression

A stopped backend caused the development proxy to return an empty HTTP 502 body. The shared browser client now reports unreadable or unavailable API responses without exposing JSON parse errors. Five focused browser tests pass (empty 502, HTML 503, empty 200, structured expiry and failed-refresh recovery), and the production build passes. The live backend was restarted separately from the tool session; direct and frontend-proxied config requests both returned valid live-mode JSON.

## Context payload performance regression

A user reported a long wait after parcel selection. A local proxy measurement for APN 2202010006 returned about 1.27 MB: cached context took 0.13 seconds and fresh context took 10.58 seconds. This did not reproduce the reported minute-long delay, but identified substantial unnecessary raw boundary geometry transferred to the browser.

The browser now requests `compact=true`, keeping map geometry and all displayed provenance while full evidence remains in the server snapshot. A contract test verifies equivalent assessment output, unchanged map/diagnostics/fingerprint, retained raw server evidence and a compact fixture payload under 30 KB and under one tenth of the full response. Loading text explains which evidence is being fetched and the live-source wait budget. This reduces transfer/parsing cost; it does not guarantee faster official-source responses.

After restarting the updated live backend, the proxied fresh compact response for 2202010006 was 8,100 bytes in 10.46 seconds; the cached response was 8,116 bytes in 0.048 seconds. Both were live-mode, resolved responses. The focused API contract test, production build and all 14 browser tests passed.

## Visible loading feedback

Search, the clicked parcel candidate and refresh controls now show a spinner and an action-specific loading label immediately. The active action is disabled while pending; other parcel selections remain available. A status message names the pending work, and reduced-motion preferences suppress animation without hiding the loading label. A browser test against the running UI with controlled synthetic delays verifies search, selection, success, refresh failure and reduced-motion transitions. The production build passes. The live backend was left running during this UI check.
