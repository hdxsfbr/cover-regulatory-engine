# Proposal

## Why

Successful live parcel lookups currently return five empty constraint cards: the application never supplies documented dimensions or applicability facts to its evaluator, and hides the reasons inside collapsed details. Public assessor maps contain useful measurements, but the user must discover and transcribe them; completed lookup tasks have not delivered the useful-assessment milestone.

## What Changes

- Automatically resolve parcel-specific assessor-map references, retrieve bounded document evidence, and expose tract/lot identity, document vintage, availability, and direct source links.
- Add a reusable, attributed document-observation/review path and populate it from inspected public maps for the two Louise acceptance parcels. Preserve the distinction between map measurements, derived area, GIS estimates, and established legal dimensions. Unreadable or unreviewed scans stay explicit; generic automatic interpretation of arbitrary survey maps is not promised.
- Retrieve named Hillside Ordinance and coastal screening layers with source-specific outcomes. Display observations without treating a layer's no-match as proof that all statutory exclusions are absent; require a documented coverage/meaning decision before using a screening result to satisfy an applicability predicate.
- Replace opaque missing-key strings with structured blockers and targeted actions visible on each constraint card. Distinguish unavailable evidence, unsupported rules, unresolved property applicability, and project inputs such as proposed height and roof slope.
- Carry evidence origin/version through server snapshots, review, calculation and refresh; prevent stale, conflicting or merely asserted evidence from acquiring verified status.
- Validate source-backed progress across real parcels, with before/after counts of manual dimensions and checks, browser inspection, and controlled failures. Do not close this change merely because every card has explanatory text: the two supported Louise cases must reuse documented dimensions without user transcription.

Regulatory scope remains the existing five ordinary-case Chapter 1 R1-1 single-family scalar rules. ADU, guest-house, other zoning, full entitlement research, arbitrary automated survey interpretation, production deployment and independent professional validation remain outside this change. Existing applicability gates remain binding.

## Capabilities

### New Capabilities

None; extend the existing parcel and assessment capabilities.

### Modified Capabilities

- `parcel-context`: Public document discovery, attributed dimension observations, bounded applicability screening, and evidence freshness.
- `buildability-assessment`: Explicit evidence acceptance, structured visible blockers and actions, and real-property acceptance gates that measure reduced user effort.

## Impact

Backend GIS/source manifest, local evidence storage and ingestion/review tooling, immutable context snapshots and fingerprints, rule input provenance and API schemas; frontend types, constraint cards, evidence/input controls and refresh handling; backend/browser fixtures and acceptance documentation. Preserve existing API fields and live/recorded separation. Reuse Python/httpx, local hashed artifacts and existing review patterns; no paid model service or new production infrastructure required. Depends on the implemented `live-parcel-assessment` behavior, which remains unarchived. Detailed baseline and source research are in this change's audit.md.
