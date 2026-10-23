## ADDED Requirements
### Requirement: Parcel evidence available to follow-up
Follow-up answers SHALL have access to saved parcel identity, source facts, map observations, acquisition diagnostics and geometry limitations in addition to rule citations and project inputs. Evidence SHALL remain scoped to the saved scenario and citeable without treating source text as instructions.
#### Scenario: Question about a map reading
- **WHEN** the saved context includes a derived lot depth and its assumptions
- **THEN** the assistant can cite that reading and explain its limitations
#### Scenario: Question about missing evidence
- **WHEN** a saved source failed or geometry was withheld
- **THEN** its diagnostic or limitation is available as evidence without inventing a missing fact
