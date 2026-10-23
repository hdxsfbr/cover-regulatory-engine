## ADDED Requirements

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
