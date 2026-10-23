# Proposal

## Why
Architects still leave the assessment to inspect planning cases, building permits, engineering records and transit access. Retrieve these public records alongside the assessment so each next lookup starts with parcel-specific evidence.

## What Changes
- Add independently loaded ZIMAS profiles and Planning case/document references, PRISM permit history, NavigateLA engineering screening and Metro stops with pedestrian route estimates.
- Show concise findings and next actions, expandable records, provenance, explicit missing/partial results and source-specific retries.
- Preserve research in saved scenarios and make it available to cited Q&A without overwriting concurrent map extraction or design inputs.
- Keep existing regulatory scope. Records and route estimates do not establish permit legality, absence of easements, utility capacity or statutory transit eligibility.

## Capabilities
### New Capabilities
None.
### Modified Capabilities
- `parcel-context`: supplemental research retrieval, association, provenance and presentation.
- `assessment-assistant`: cite saved supplemental research.

## Impact
Python source adapters and snapshot API; frontend research panel and context merge; scenario evidence and Q&A; source fixtures, backend/browser tests and access report. Reuse HTTP, geometry and persistence dependencies. External reads use official public services plus the publicly documented Valhalla pedestrian routing service, explicitly attributed to OpenStreetMap.
