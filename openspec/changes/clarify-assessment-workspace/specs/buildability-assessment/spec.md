## ADDED Requirements

### Requirement: Decision-ordered assessment workspace
The interface SHALL distinguish matching candidates from a selected property. Once selected, it SHALL prioritize property identity, project type, map, assessment summary and compact comparable constraints ahead of detailed sources and project management. Primary blockers and coverage limits SHALL remain visible, with supporting evidence available on demand.

#### Scenario: Select a search result
- **WHEN** a search returns candidates
- **THEN** each has an explicit open-assessment action and selection shows loading immediately, then replaces candidate clutter with the selected identity and a change-property action

#### Scenario: Inspect the selected assessment
- **WHEN** context is available
- **THEN** the map and summary precede compact constraints, each with result, units, status and access to all existing derivations, assumptions, confidence, citations and map linkage

#### Scenario: Next action and uncertainty
- **WHEN** results need project inputs, evidence inspection or source recovery
- **THEN** actionable controls open and focus the relevant section without treating unsupported coverage or unknown assertions as completed facts

#### Scenario: Background evidence
- **WHEN** a map-reading job is running, cancelled or fails
- **THEN** progress and cancel or retry remain visible without requiring the user to expand the evidence section

#### Scenario: Accessible responsive layout
- **WHEN** the workspace is used by keyboard or at a 390-pixel viewport
- **THEN** property selection, project inputs, disclosures, map links and recovery controls remain usable without page-level horizontal scrolling or color-only meaning
