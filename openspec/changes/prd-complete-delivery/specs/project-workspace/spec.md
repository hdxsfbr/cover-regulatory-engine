## Purpose

Let architects persist evolving parcel projects, compare evidence-backed scenarios and submit attributable feedback on specific results.

## ADDED Requirements

### Requirement: Durable project scenarios
Users SHALL save project scenarios with parcel identity, project classification, design inputs, explicit assumptions and immutable assessment/evidence/rule references. Reopening after restart SHALL retain those versions. New source information SHALL create a new current assessment without silently rewriting prior scenarios.

#### Scenario: Save and compare
- **WHEN** a user saves two designs with different supported parameters
- **THEN** both survive restart and comparison identifies changed inputs, dependent constraints, geometry and any evidence-version differences

#### Scenario: Stale saved scenario
- **WHEN** source evidence is superseded
- **THEN** historical results remain attributable to their original version and the user is offered reassessment rather than being shown the old result as current

### Requirement: Result-linked feedback
Users SHALL submit feedback against an identified assessment, constraint or source. Feedback SHALL persist with its target version, text and review state, and appear in the operator workflow. Feedback SHALL not directly modify a reviewed rule or verified fact.

#### Scenario: Disputed result
- **WHEN** a user reports an incorrect constraint and its basis
- **THEN** the operator can inspect the exact disputed result and sources, track the response and link any separately reviewed correction

### Requirement: Workspace isolation and usable controls
Project inputs, jobs, follow-up context and feedback SHALL remain scoped to their project. Core interactions SHALL work by keyboard and on mobile; source/job failures SHALL preserve user work and provide explicit recovery controls.

#### Scenario: Concurrent projects
- **WHEN** two projects are open while acquisition or assessment requests complete out of order
- **THEN** each result and follow-up context stays associated with its own project and current revision
