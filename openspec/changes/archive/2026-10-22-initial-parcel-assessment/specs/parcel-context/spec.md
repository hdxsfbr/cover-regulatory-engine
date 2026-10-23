# Spec Delta

## Purpose

Resolve a user's property and assemble traceable parcel, jurisdiction, zoning, overlay, and building facts for downstream assessment.

## ADDED Requirements

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
