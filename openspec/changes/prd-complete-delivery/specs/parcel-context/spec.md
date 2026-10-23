## ADDED Requirements

### Requirement: General live evidence acquisition
Every resolved LA residential parcel SHALL use the same identity-based public evidence acquisition workflow, including available assessor and referenced land-record documents. A live attempt SHALL NOT require a prewritten observation record or per-address code. Missing, blocked and unavailable sources SHALL retain distinct outcomes and direct evidence references.

#### Scenario: Unseen address
- **WHEN** a user searches a residential parcel absent from stored observations and example prompts
- **THEN** the system discovers and attempts its available documents and returns source-backed facts or specific acquisition failures without a developer adding that parcel

#### Scenario: Referenced document retrieval
- **WHEN** an acquired map identifies a further relevant record
- **THEN** the system follows supported references within approved host, page, byte and time limits and reports unresolved references rather than inventing their contents

### Requirement: Grounded automatic map observations
The system SHALL identify the searched lot before extracting dimensions from text or scanned documents. Each proposed observation SHALL retain document version, page/region, source marking, units, extraction method and uncertainty. Validation SHALL check identity, arithmetic and spatial consistency; machine validation SHALL remain distinct from human or legal review.

#### Scenario: Multi-lot scanned sheet
- **WHEN** a sheet contains several lots, repeated dimensions or ditto marks
- **THEN** extracted measurements identify the target lot and supporting markings, and ambiguous assignments are withheld for focused review

#### Scenario: Irregular lot and geometry mismatch
- **WHEN** a document reading conflicts with lot shape or front/rear/side classification
- **THEN** the system identifies the disagreement and does not substitute a longest edge, uniform rectangle or neighboring lot measurement

### Requirement: Persistent bounded evidence jobs
Slow extraction SHALL run independently of the initial parcel response, with visible stages, cancellation, terminal errors and bounded retries. Jobs and immutable evidence SHALL survive restart and deduplicate repeated requests. Completed evidence SHALL update only the matching current parcel/scenario and retain source-version invalidation.

#### Scenario: Slow model or restart
- **WHEN** extraction is pending, cancelled, interrupted by restart or exceeds its 240-second budget
- **THEN** known context remains usable and the job resumes safely or reports an explicit terminal state without an indefinite spinner or fabricated result

#### Scenario: Repeated search
- **WHEN** identical identity and source content are requested again
- **THEN** the existing valid extraction is reused with its provenance, while a changed document creates a new version and invalidates dependent current facts
