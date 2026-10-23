# Proposal

## Why

The current project demonstrates a narrow evaluator and evidence UI but does not deliver the PRD's general parcel-to-assessment workflow. Search-time map interpretation, substantive ADU/guest-house support, useful synthesis, scenario persistence, feedback, grounded follow-up, setback geometry and an admin demonstration are incomplete or absent; two seeded properties and completed incremental checklists are not product acceptance.

## What Changes

- Deliver against a requirement-by-requirement PRD matrix and a frozen unseen-parcel acceptance cohort; all six bonus features are included in the user's requested full-feature release.
- Generalize property resolution and automatic document/evidence acquisition, lot identification, machine-assisted dimension extraction and corroboration for any searched LA residential parcel. No per-address seed file or code edit is allowed on the acceptance path.
- Replace formula-fed extraction with source-driven candidate rule synthesis, cross-reference/precedence handling, review and deterministic execution. Implement meaningful bounded single-family, new detached ADU and detached guest-house rule packages.
- Separate sourced facts, validated extractions, interpretations and project assumptions; provide cited conditional decision paths instead of requiring blanket assertions to see any useful result.
- Add a persistent project/scenario workspace, grounded follow-up interface, feedback, map annotations and supported setback envelopes, and a minimal admin ingestion/review UI.
- Deliver a reproducible full-feature POC, performance/evidence benchmarks, install/demo instructions and an actionable production architecture; do not mistake a proposed production diagram for a production deployment.

The PRD explicitly allows a small reasoned subset of regulations; this plan does not promise every LA zone, every ADU variant or complete building-code/permit compliance. It does require the same general evidence workflow for every address, meaningful positive cases for all three named project types, explicit unresolved outcomes and all bonus surfaces. Arbitrary parcels are not promised guaranteed legally conclusive numbers. See docs/prd-delivery-plan.md for exact scope, timing, evidence criteria and dependencies.

## Capabilities

### New Capabilities

- `project-workspace`: Durable project scenarios, input revisions, comparison and feedback tied to assessment versions.
- `assessment-assistant`: Cited questions and explanations grounded in the current parcel, project and regulatory evidence.
- `regulatory-review`: Operator UI for acquisition, extraction, source comparison, corrections, activation and audit history.

### Modified Capabilities

- `source-recovery`: Preserve reviewed project-package scope during retry rather than the superseded blanket accessory exclusion.

- `parcel-context`: General automatic document interpretation and reusable parcel evidence jobs rather than curated address records.
- `regulatory-rules`: Source-driven synthesis, cross-reference/precedence resolution and bounded rules for all three project types.
- `buildability-assessment`: Project-aware coverage, conditional interpretations, spatial envelopes, generalization and whole-product acceptance.

## Impact

Backend GIS, evidence, ingestion, rule schema/evaluator and API; React/Leaflet UI; durable local POC storage and bounded background jobs; source manifests and versioned artifacts; backend, browser and adversarial evidence tests; demo, architecture, requirements traceability and delivery reporting. Retain working provenance, refresh, timeout, rule-review and stale-response protections. Migrate existing local JSON explicitly and reconcile completed-but-unarchived deltas before final spec synchronization. No paid provider fallback or public infrastructure provisioning is authorized by this plan. Existing Claude use remains subscription-only; application model work requires a functioning supported local adapter and a measured feasibility check, not an assumed hosted subscription API.
