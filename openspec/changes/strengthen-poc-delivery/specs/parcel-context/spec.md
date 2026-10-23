## ADDED Requirements
### Requirement: Reusable document readings
The system SHALL reuse map-reading jobs for unchanged parcel identity, document content, geometry, code regime and extraction/derivation versions within a daily freshness window. Acquisition timestamps alone SHALL not force rereading. Changed validation inputs SHALL invalidate reuse.
#### Scenario: Same document reacquired
- **WHEN** only acquisition timestamps change within the freshness window
- **THEN** the existing extraction job is reused without another model call
#### Scenario: Validation context changed
- **WHEN** map content, parcel geometry, identity, regime or extraction version changes
- **THEN** the prior extraction is not reused
