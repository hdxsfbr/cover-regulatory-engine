## ADDED Requirements

### Requirement: Proposal outcomes beside limits
Constraint rows SHALL show available backend design comparisons beside their limits, including proposed quantity, outcome and excess, without confusing evaluated evidence with a compliant design. Conditional and missing-input comparisons SHALL retain uncertainty.

#### Scenario: Height exceeds limit
- **WHEN** a 19 ft design is compared with an evaluated 16 ft limit
- **THEN** the height row shows the proposal, limit and 3 ft excess and the primary next action focuses the height input

#### Scenario: Conditional limit
- **WHEN** a comparison depends on unresolved applicability
- **THEN** its conditional status and evidence remain visible without implying compliance

### Requirement: Available map actions
A constraint SHALL offer Locate on map only when the current geometry contains an annotation for that category.

#### Scenario: Withheld geometry
- **WHEN** setback geometry is withheld or no category annotation exists
- **THEN** the row offers no misleading map action and the geometry explanation remains available
