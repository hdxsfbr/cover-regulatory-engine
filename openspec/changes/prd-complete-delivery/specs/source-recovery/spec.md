## MODIFIED Requirements

### Requirement: Preserve regulatory scope during recovery
Recovery SHALL NOT change the supported rule set, promote user assertions to verified facts, or turn empty overlay results into complete applicability verification. The selected package's constraint categories SHALL remain visible; reviewed ADU and guest-house branches SHALL use their own rules, while Chapter1A and uncovered variants remain unsupported.

#### Scenario: Recovery with unsupported project
- **WHEN** a new context is successfully retrieved for an uncovered project variant
- **THEN** the map and source evidence update but that variant's regulatory calculations remain unsupported
