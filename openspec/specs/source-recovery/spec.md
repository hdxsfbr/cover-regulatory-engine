# source-recovery Specification

## Purpose

Help users distinguish recorded evidence from live property queries and recover from unavailable sources without confusing missing data with regulatory findings.

## Requirements

### Requirement: Explicit data mode
The interface SHALL identify live or recorded mode before lookup and on the result. Recorded mode SHALL explain that refreshing replays saved evidence; it SHALL NOT present replay as a new upstream request. Live mode SHALL never substitute recorded fixtures for failed sources.

#### Scenario: Replay of recorded failure
- **WHEN** a user views recorded APN 2202010006 with unavailable Chapter 1 zoning
- **THEN** the result identifies recorded evidence and explains that replay cannot obtain updated zoning

#### Scenario: Live source failure
- **WHEN** an official source fails in live mode
- **THEN** its unavailable state remains visible without replacing it with fixture data

### Requirement: Specific evidence diagnostics
The system SHALL distinguish unavailable source, source not checked, invalid geometry, no zoning match, coverage gap and multiple positive zone matches using stable reason codes and understandable text. Each diagnostic SHALL identify its relevant source or spatial evidence. A failed query alone SHALL NOT be described as a zoning conflict.

#### Scenario: Unavailable zoning source
- **WHEN** Chapter 1 zoning is unavailable and no positive zoning matches were returned
- **THEN** the result identifies missing zoning-source evidence and withholds calculation without claiming conflicting zoning

#### Scenario: Actual spatial ambiguity
- **WHEN** complete queries return multiple positive zone matches or uncovered parcel area
- **THEN** the result identifies those spatial conditions, retains all matches and withholds dependent calculations

### Requirement: Explicit fresh context
In live mode, users SHALL be able to request fresh whole-parcel context that bypasses cached context and produces a new snapshot. Existing snapshots SHALL remain unchanged until their normal expiry or eviction. Successful and failed sources SHALL retain separate statuses and retrieval times; a failed retry SHALL NOT silently restore a prior success as current.

#### Scenario: Cached success followed by fresh failure
- **WHEN** an explicit fresh request encounters a source failure after a cached successful lookup
- **THEN** the new snapshot reports that failure and the old snapshot is not mutated or substituted

#### Scenario: Recovery from unavailable source
- **WHEN** a fresh lookup succeeds after a previous source timeout
- **THEN** the new context contains newly retrieved evidence and is reassessed against its new snapshot

### Requirement: Consistent project state during recovery
Refreshing the same parcel SHALL preserve project type, entered dimensions and their evidence note, mark assessment pending, and assess only the replacement snapshot. Applicability assertions SHALL be cleared with an explanation when relevant jurisdiction, zoning or overlay evidence changes. Selecting another parcel SHALL clear parcel-specific inputs and assertions.

#### Scenario: Same parcel and unchanged evidence
- **WHEN** a fresh lookup returns equivalent applicability evidence for the same parcel
- **THEN** project entries and assertions remain available and the new assessment identifies the new snapshot

#### Scenario: Changed or newly unavailable applicability evidence
- **WHEN** fresh jurisdiction, zoning or selected-overlay evidence differs or becomes unavailable
- **THEN** dimensions and their note remain but applicability assertions are cleared, affected results are withheld, and the user is asked to review the changed evidence

#### Scenario: Late response
- **WHEN** an older lookup or assessment finishes after a newer parcel selection or retry
- **THEN** it does not overwrite the newer context, inputs or result

### Requirement: Bounded actionable recovery
Fresh lookup SHALL exit loading within 30 seconds, preserve completed independent source results and offer an accurately labeled whole-context retry in live mode. Missing parcel geometry and expired snapshots SHALL have usable recovery controls. Retries SHALL be user initiated, not an unbounded automatic loop.

#### Scenario: Parcel source unavailable
- **WHEN** a selected parcel lookup fails before returning parcel attributes or geometry
- **THEN** the selected identifier remains available to retry and downstream sources remain explicitly not checked or unavailable as appropriate

#### Scenario: Snapshot expired
- **WHEN** assessment reports an expired snapshot
- **THEN** the interface explains expiry and offers fresh context recovery without discarding entered dimensions for that parcel

#### Scenario: Slow source
- **WHEN** a source exceeds the lookup budget
- **THEN** the interface exits loading with its specific failure, retains completed evidence and permits a new bounded attempt

### Requirement: Preserve regulatory scope during recovery
Recovery SHALL NOT change the supported rule set, promote user assertions to verified facts, or turn empty overlay results into complete applicability verification. The selected package's constraint categories SHALL remain visible; reviewed ADU and guest-house branches SHALL use their own rules, while Chapter1A and uncovered variants remain unsupported.

#### Scenario: Recovery with unsupported project
- **WHEN** a new context is successfully retrieved for an uncovered project variant
- **THEN** the map and source evidence update but that variant's regulatory calculations remain unsupported
