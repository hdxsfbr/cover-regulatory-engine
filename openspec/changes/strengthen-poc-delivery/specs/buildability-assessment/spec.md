## ADDED Requirements
### Requirement: Research guidance and contextual inputs
Inputs SHALL distinguish source-backed applicability facts from user assertions, explain evidence needed for unresolved checks and identify contextual-only fields. Automatic facts SHALL retain uncertainty and permit explicit override.
#### Scenario: Source resolves a check
- **WHEN** available source evidence establishes a supported applicability fact
- **THEN** the input guidance shows the source-backed state and limitation without requiring redundant user research
#### Scenario: Unsupported automation
- **WHEN** a check needs information the sources do not establish
- **THEN** the UI describes the needed evidence without inventing a resolution
#### Scenario: Contextual design field
- **WHEN** bedrooms or stories do not drive current calculations
- **THEN** the field is labeled contextual-only
