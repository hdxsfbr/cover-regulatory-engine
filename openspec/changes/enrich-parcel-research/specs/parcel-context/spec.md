## ADDED Requirements

### Requirement: Supplemental parcel research
The system SHALL retrieve ZIMAS profile and Planning case references, PRISM permit history, NavigateLA engineering features and Metro transit candidates for any resolved parcel using identity or documented spatial matching. Records SHALL retain source links, retrieval time, association method and coverage limitations.

#### Scenario: Public records available
- **WHEN** a parcel has matching official records
- **THEN** the assessment shows useful record details and available document links without another manual search

#### Scenario: Association uncertainty
- **WHEN** an APN resolves to multiple city parcels or an engineering feature is only nearby
- **THEN** the association is explicit and no neighboring record is represented as a verified parcel restriction

### Requirement: Independent research recovery and retention
Supplemental sources SHALL load independently without blocking existing results or extraction. Loading, matched, no-match, partial, unavailable and recorded states SHALL be distinct. Retry SHALL preserve other evidence and inputs. Saved scenarios SHALL retain the research shown at save time, and late responses SHALL NOT change another parcel or overwrite completed map readings.

#### Scenario: One source fails
- **WHEN** PRISM fails while other sources succeed
- **THEN** successful evidence remains visible and a PRISM retry is available without repeating other lookups

#### Scenario: Concurrent extraction and navigation
- **WHEN** map extraction completes during research loading or the user switches parcels
- **THEN** completed readings are preserved and research is attached only to its original parcel context

### Requirement: Transit and engineering screening boundaries
The system SHALL distinguish transit stop proximity, estimated pedestrian distance and regulatory qualification. Route origin, provider and limitations SHALL be visible. Engineering matches and permit history SHALL NOT automatically establish utility capacity, legal clearance, lawful structures or absence of restrictions.

#### Scenario: Nearby Metro stop
- **WHEN** a stop and a pedestrian route are retrieved
- **THEN** the user sees the stop, distances and route evidence while statutory transit eligibility remains unresolved

#### Scenario: Missing route or truncated records
- **WHEN** routing fails or a bounded source response is truncated
- **THEN** retrieved records remain available with an explicit incomplete status and source-specific next action
