# regulatory-rules Specification

## Purpose

Transform selected official regulatory text into versioned, reviewed rules whose evidence and applicability can be inspected and reproduced.

## Requirements

### Requirement: Versioned regulatory sources
The system SHALL preserve the selected source text with publisher, URL, section identifier, retrieval time, content hash, and known edition or effective-date information. Missing dates and unresolved cross-references SHALL be explicit. A citation SHALL resolve to a passage in the preserved source and a public source link.

#### Scenario: Source changes
- **WHEN** a newly retrieved section has a different content hash
- **THEN** it is recorded as a new version without overwriting the source used by existing rules

### Requirement: LLM-assisted candidate extraction
An ingestion operation SHALL use an LLM to derive candidate rules from selected text with source spans, expressions, applicability predicates, required inputs, units, exceptions and cross-references. Prompts SHALL provide schemas and allowed operations rather than predetermined answers. Source text SHALL be treated as data and SHALL NOT authorize tools, executable code or external actions.

#### Scenario: Extract a dimensional rule
- **WHEN** a selected passage states a dimensional requirement
- **THEN** extraction derives a candidate with the relevant expression, passage, units, conditions and exception references for review without being supplied the expected threshold or formula

#### Scenario: Invalid model output
- **WHEN** output has a missing citation, unsupported operation, invalid units, or a quoted passage absent from the source
- **THEN** validation rejects it and it cannot be activated

#### Scenario: Changed source threshold
- **WHEN** a controlled source test changes a threshold or condition
- **THEN** extraction reflects that changed passage or reports a validation conflict, and activation still requires new review

### Requirement: Reviewed activation
Only explicitly reviewed rules with validated citations, supported operations, and resolved applicability dependencies SHALL be eligible for evaluation. Review SHALL record reviewer, time, rule version, and source versions. Re-extraction or source changes SHALL create candidates requiring new review rather than altering an active rule silently.

#### Scenario: Incomplete exception handling
- **WHEN** a candidate depends on an unresolved exception or unavailable applicability fact
- **THEN** it remains ineligible for activation until its dependency is resolved or an explicit supported-scope exclusion is reviewed

#### Scenario: Superseded source
- **WHEN** an active rule's source is known to be superseded
- **THEN** current assessments withhold that rule pending review while historical assessments retain their original evidence

### Requirement: Initial rule coverage
The initial reviewed rule set SHALL cover front, side, and rear yards, height, and residential floor-area limits for a documented subset of conventional Chapter 1 R1 single-family projects. Each rule SHALL state its supported conditions and inputs; unsupported variations SHALL not inherit a generic value.

#### Scenario: Supported rule set
- **WHEN** the initial rule set is prepared for acceptance
- **THEN** all five constraint categories have source-backed reviewed rules and passing positive and excluded-applicability examples

#### Scenario: R1 variation or additional condition
- **WHEN** a property has a zone variation, prefix, suffix, or other condition outside a rule's reviewed scope
- **THEN** that rule does not supply an unconditional numeric limit

### Requirement: Reproducible extraction evidence
The ingestion operation SHALL record model identifier, extraction instructions version, validation outcome, and source versions. Assessment of an already reviewed rule set SHALL work without a live LLM call or provider credentials.

#### Scenario: Provider unavailable
- **WHEN** the model provider is unavailable during ingestion
- **THEN** ingestion reports the failure without creating approved rules, and assessments using the existing reviewed set remain available

### Requirement: Three bounded project rule packages
The system SHALL provide reviewed positive evaluation paths for conventional single-family main buildings, new detached ADUs with an existing primary dwelling, and a documented detached guest-house category. Each package SHALL define project/use classification, supported zoning, source versions, necessary constraints and exclusions. An always-unsupported package SHALL not count as coverage.

#### Scenario: Positive project coverage
- **WHEN** each named package is presented for release acceptance
- **THEN** it has at least two source-backed positive scenarios and an exception or excluded branch, with independent expected results and no substitution of main-building rules under another label

#### Scenario: Misclassified accessory proposal
- **WHEN** proposed use characteristics do not meet the chosen package's sourced definition
- **THEN** the system identifies the classification conflict and the relevant alternative or unsupported branch before applying dimensional rules

### Requirement: Dependency and precedence synthesis
Reviewed rules SHALL retain jurisdiction, regime, effective-date basis, cross-references, exceptions and applicable precedence. Individual applicability facts SHALL identify supporting evidence or unresolved interpretation. Missing dependencies and conflicting authorities SHALL not be resolved by an undocumented model preference or a blanket user assertion.

#### Scenario: State and local interaction
- **WHEN** a selected project depends on state and local provisions
- **THEN** the applicable relationship and controlling source are inspectable with citations, or that branch remains unresolved with the specific dependency named

#### Scenario: Unresolved fact
- **WHEN** available records establish some required conditions but not another
- **THEN** established facts are reused and only the unresolved condition is requested or included as an explicit conditional assumption
