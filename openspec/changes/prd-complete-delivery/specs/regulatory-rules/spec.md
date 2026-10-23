## MODIFIED Requirements

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

## ADDED Requirements

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
