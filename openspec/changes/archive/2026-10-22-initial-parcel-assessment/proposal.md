# Proposal

## Why

Architects need to trace a parcel assessment back to the facts and regulatory passages that produced it. The repository currently contains only the brief and workflow setup; an end-to-end assessment will demonstrate that regulatory ingestion can produce useful, inspectable constraints from real LA data.

## What Changes

- Resolve a residential address or APN, establish LA City jurisdiction, and display parcel geometry and mapped building footprints.
- Identify Chapter 1 versus Chapter 1A zoning and check historic preservation, specific-plan, and community-design overlay layers; preserve complete zone strings and ambiguous spatial matches.
- Ingest selected official Chapter 1 text using an LLM to propose structured, cited rule fragments, validate them, and require explicit review before deterministic evaluation.
- Initially support conventional Chapter 1 R1 single-family projects: front, side, and rear yard requirements, height, and residential floor-area limits, including applicability predicates and referenced exceptions needed for each supported rule. Enable a rule only after its source dependencies and required parcel/project facts have been verified.
- Return per-constraint evidence, confidence reasons, and evaluated/needs-review/unsupported outcomes. ADU, guest-house, Chapter 1A, and unmodeled conditional or overlay cases retain parcel context but receive explicit unsupported or review outcomes.
- Validate the flow with independently checked sample parcels, boundary ambiguity, source failures, and multiple requested building types; document a production architecture.
- Out of scope: comprehensive legal buildability or permit approval, construction-code compliance, complete overlay coverage, automatic setback geometry, chat, user accounts, feedback/admin interfaces, and deployment infrastructure.

## Capabilities

### New Capabilities

- `parcel-context`: Parcel resolution, jurisdiction, zoning, selected overlays, mapped buildings, and source provenance.
- `regulatory-rules`: Versioned regulatory sources, LLM extraction, validation, and reviewed rule activation.
- `buildability-assessment`: Deterministic rule application, evidence and uncertainty reporting, and an interactive assessment interface.

### Modified Capabilities

None; no existing capability specs are present.

## Impact

Adds a Python backend and TypeScript frontend, read-only integrations with County GIS and City zoning services, a regulatory ingestion command, and evaluation fixtures. Proposed implementation uses FastAPI, React, Leaflet, Shapely, and local versioned source/rule artifacts; final dependency versions are selected during implementation. The first change is a scoped demonstration: ADU and guest-house calculations remain future work, so it does not establish full building-type coverage for the overall brief.
