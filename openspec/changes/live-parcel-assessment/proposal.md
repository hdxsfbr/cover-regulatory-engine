# Proposal

## Why

The prototype already supports live GIS, but the running recorded demo makes a saved source failure look like a property finding. Generic zoning warnings, cache-backed refresh and controls that reset project inputs make it difficult to understand and recover from real source failures.

## What Changes

- Make live versus recorded mode unmistakable, with documented live startup and clearly labeled replay behavior in fixture mode.
- Distinguish missing source data, invalid geometry, coverage gaps and conflicting zone matches using specific, source-linked diagnostics.
- Add an explicit fresh-context request that bypasses the successful GIS cache, keeps the shared lookup budget, creates a new server-owned snapshot and does not overwrite a previous snapshot.
- Make recovery controls describe their actual scope: retrying any layer refreshes the whole context. Preserve entered project information for the same parcel, but invalidate the old assessment and reset applicability assertions if relevant jurisdiction/zoning/overlay evidence changes.
- Test timeout-to-recovery, true spatial ambiguity, unsuccessful retries, expired snapshots, mode labeling and late response races.
- Regulatory scope stays at the five reviewed ordinary-case R1-1 single-family constraints. ADU, guest-house, Chapter 1A calculations, new automatic applicability sources, geocoding, persistence and deployment are outside this change.

## Capabilities

### New Capabilities

- `source-recovery`: Explicit data mode, diagnostic reasons and bounded fresh-context recovery with consistent project and snapshot state.

### Modified Capabilities

None. The initial change's parcel-context and buildability-assessment contracts remain intact; this additive capability specifies recovery behavior in greater detail. The completed initial change was synchronized and archived on 2026-10-22; its three main specs are the baseline.

## Impact

Touches `backend/gis.py`, `backend/app.py`, `frontend/src/main.tsx`, nearby tests, README and API/demo documentation. Reuses current HTTP clients, finite evaluator, 15-minute caches and snapshot identifiers. Adds a backward-compatible fresh query option to the context endpoint and structured diagnostics while retaining existing status fields and human-readable issues. No new dependencies are expected.

This is phase 1 of `openspec/roadmap.md`. Later phases remain separately scoped changes with evidence gates, rather than promises that unresearched regulations are already implementable.
