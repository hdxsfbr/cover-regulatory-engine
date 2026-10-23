# parcel-context Specification

## Purpose

Resolve a user's property and assemble traceable parcel, jurisdiction, zoning, overlay, and building facts for downstream assessment.

## Requirements

### Requirement: Address and APN resolution
The system SHALL resolve an address or APN to parcel candidates, normalize formatted APNs, and require selection when multiple candidates match. Invalid input, no match, and unavailable sources SHALL remain distinct outcomes.

#### Scenario: Formatted APN
- **WHEN** a user enters an APN with or without separators
- **THEN** the same parcel candidates are returned with APN and available address labels

#### Scenario: Ambiguous address
- **WHEN** an address matches multiple parcels
- **THEN** the system presents candidates and does not silently select one

#### Scenario: Failed lookup
- **WHEN** the parcel service times out
- **THEN** the user receives an unavailable-source outcome rather than a no-match result

### Requirement: Jurisdiction verification
The system SHALL establish jurisdiction from parcel geometry and boundary evidence before evaluating LA City rules. Outside-city and unresolved boundary cases SHALL not receive an LA City regulatory evaluation.

#### Scenario: Postal address differs from jurisdiction
- **WHEN** an address is labeled Los Angeles but the parcel is outside the City boundary
- **THEN** the system reports outside supported jurisdiction regardless of the postal city

#### Scenario: Boundary uncertainty
- **WHEN** jurisdiction cannot be established because of missing geometry, failed service, or conflicting boundary matches
- **THEN** the system reports jurisdiction needs review and withholds dependent rules

### Requirement: Complete zoning and spatial ambiguity
The system SHALL query both zoning regimes, preserve complete designations and all spatial matches, and report overlap areas and fractions. Tiny intersections SHALL be flagged as possible alignment artifacts, not silently discarded or asserted to be legal split zoning. Ambiguous zoning SHALL prevent dependent rule evaluation.

#### Scenario: Rhea Court boundary sliver
- **WHEN** the recorded APN 2126-037-055 fixture intersects (T)(Q)RD5-1-RIO over approximately 99.995% and R1-1-RIO over approximately 0.0011%
- **THEN** both matches and their source geometry evidence are retained, with the smaller match flagged as a possible sliver and zoning requiring review

#### Scenario: Two zoning regimes
- **WHEN** a parcel materially intersects both Chapter 1 and Chapter 1A layers
- **THEN** the system reports conflicting or split coverage needing review rather than choosing a regime

### Requirement: Selected overlay coverage
The system SHALL check historic-preservation, specific-plan, and community-design overlays independently and expose matched, no-match, unavailable, and not-checked states. It SHALL enumerate checked layers and SHALL NOT equate no matches in these layers with absence of all restrictions.

#### Scenario: Partial overlay failure
- **WHEN** historic and design checks succeed but the specific-plan service fails
- **THEN** the successful results remain visible and the specific-plan status is unavailable

### Requirement: Source provenance and mapped buildings
Parcel facts and building footprints SHALL include source URL, retrieval time, available source vintage, and live/cached/fixture origin. Geometry SHALL have an identified coordinate reference system. Unknown vintage SHALL be explicit; mapped footprints SHALL not be presented as proof of current or permitted structures.

#### Scenario: Historic footprints
- **WHEN** a building is returned from LARIAC Buildings 2020
- **THEN** it is displayed as a mapped footprint from that dataset with its vintage visible

#### Scenario: Missing footprint source
- **WHEN** footprint retrieval fails
- **THEN** parcel geometry remains available and the building state is unavailable rather than no buildings

### Requirement: Parcel-specific public document discovery
For a resolved parcel, the system SHALL expose its available assessor map, tract and lot identifiers and retrieve the referenced assessor sheet with source URL, retrieval time, content hash and available document vintage. Unavailable, unreferenced and available documents SHALL be distinct states. Document requests SHALL preserve the existing bounded lookup and live/recorded behavior.

#### Scenario: Louise assessor sheet
- **WHEN** APN 2202010006 resolves with assessor map 2202-010 and Tract 16180 Lot 108
- **THEN** its public sheet is directly accessible from the parcel evidence, attributed to that identity, with retrieval status and vintage independent of the current lookup date

#### Scenario: Missing or failing document
- **WHEN** a parcel has no valid map reference or its document source fails
- **THEN** the UI distinguishes missing reference from failed retrieval, keeps successful GIS evidence visible and offers the appropriate source-specific action without inventing measurements

#### Scenario: Unsafe or oversized response
- **WHEN** a reference is malformed, a redirect leaves approved source hosts, or a document response exceeds the configured size/time budget or has invalid content
- **THEN** the response is rejected as document-unavailable without arbitrary server-side fetching or blocking the parcel result past its response budget

### Requirement: Attributed parcel dimension observations
Document measurements SHALL retain parcel and lot identity, value, units, page/location, document hash, extraction method and review attribution. Observed dimensions, derived area, GIS estimates and legal interpretation SHALL be distinguishable. Unreviewed or ambiguous observations SHALL not become verified legal inputs.

#### Scenario: Reviewed map reading
- **WHEN** a reviewed observation identifies Lot 108's 50-foot width and 120-foot depth on assessor sheet 2202-010
- **THEN** those measurements are shown with the document location and review scope, and 6000 square feet is labeled derived from dimensions rather than quoted from the map

#### Scenario: Irregular or different lot
- **WHEN** the sheet contains multiple lots or a nonrectangular lot such as Lot 107
- **THEN** the system does not transfer another lot's dimensions or derive a rectangular area without supported geometry and orientation evidence

### Requirement: Named applicability screening evidence
The system SHALL retrieve Hillside Ordinance and Coastal Commission Permit Area observations with query geometry, identified CRS, feature identity, source provenance and matched/no-match/unavailable/not-checked states. It SHALL distinguish screening observations from statutory applicability and SHALL NOT infer a cleared legal predicate from a no-match without a reviewed source-coverage and meaning basis.

#### Scenario: Louise negative screening
- **WHEN** complete queries return no features for the Louise parcel
- **THEN** the two no-match observations are displayed by name, while any unresolved statutory coverage or meaning remains an explicit blocker

#### Scenario: Failed or partial screening
- **WHEN** a source fails, is truncated, or has unusable geometry
- **THEN** its result is unknown/unavailable rather than outside the regulated area, and independent successful observations remain usable

#### Scenario: Positive screening
- **WHEN** a parcel intersects a screening polygon
- **THEN** the matched feature is retained and dependent ordinary-case applicability is flagged for review rather than cleared

### Requirement: Evidence changes invalidate dependent acceptance
Document and screening versions SHALL participate in evidence freshness and applicability comparison. Changes, conflicts, expiry and failed refreshes SHALL prevent stale observations or review decisions from silently remaining current. Existing user dimensions and notes SHALL be retained with their provenance for reconsideration.

#### Scenario: Revised map or conflicting measurement
- **WHEN** a current document differs from the reviewed hash or another source conflicts with the accepted measurement
- **THEN** dependent acceptance is invalidated and the conflict or changed source is shown before another dependent calculation

#### Scenario: Recorded evidence
- **WHEN** recorded mode is active
- **THEN** document and screening results are explicitly recorded, reproducible without network access, and never represented as a fresh public-source retrieval

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
