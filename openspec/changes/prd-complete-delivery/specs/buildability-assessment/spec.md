## MODIFIED Requirements

### Requirement: Applicability and coverage gates
The system SHALL withhold unconditional calculations for ambiguous zoning, unknown applicability or unmodeled conditions. Named supported project branches SHALL use their own reviewed rules; Chapter 1A and uncovered variants SHALL remain explicitly unsupported. Every assessment SHALL state checked sources, coverage and assumptions without asserting overall legal buildability.

#### Scenario: Unsupported building type
- **WHEN** a selected project variant has no reviewed rule package
- **THEN** the parcel evidence remains visible and the system identifies the uncovered variant without implying that supplying dimensions will enable it

#### Scenario: Overlay found
- **WHEN** a checked overlay applies but its effect is not modeled
- **THEN** affected constraints need review with the overlay identified and no unconditional numeric answer

#### Scenario: Unknown hillside applicability
- **WHEN** a rule requires a non-hillside parcel but that fact has not been established
- **THEN** the unconditional rule is withheld and the missing applicability evidence is reported

### Requirement: Bounded interactive responses
Assessment SHALL use reviewed rules rather than request-time legal rule extraction. Initial external context failures SHALL produce actionable partial or unavailable states within 30 seconds. Longer document jobs SHALL expose bounded progress separately. Loaded scenario evaluation SHALL complete within one second at the 95th percentile over 100 runs on the documented machine.

#### Scenario: Slow upstream source
- **WHEN** an upstream context service does not respond within its budget
- **THEN** the interface exits context loading with a source-specific unavailable state and permits retry while any independent document job shows its own status

#### Scenario: Project edit
- **WHEN** a user changes a supported design input with facts and rules loaded
- **THEN** dependent calculations update without repeating source ingestion and the result retains its evidence versions

## ADDED Requirements

### Requirement: Structured summary and conditional decisions
An assessment SHALL summarize project classification, governing constraints, proposed-design implications and remaining decisions. Sourced facts, extracted observations, interpretations and user assumptions SHALL remain distinguishable. Conditional answers SHALL enumerate assumptions and supporting rules separately from established results, with citations and consequences for each branch.

#### Scenario: Useful partial assessment
- **WHEN** a parcel has established facts and unresolved applicability
- **THEN** the user sees resolved constraints, the precise remaining decisions and supported conditional branches without needing to assert every condition merely to inspect the reasoning

#### Scenario: Conditional answer provenance
- **WHEN** a scenario assumes an unresolved condition
- **THEN** its values and geometry are visibly conditional and cannot be exported or repeated as verified findings

### Requirement: Supported setback geometry and map linkage
For supported lot and project conditions, the system SHALL generate source-attributed setback geometry from established edge roles and applicable rules, with units, CRS and evidence versions. Constraint and map selection SHALL be linked. Missing orientation or contradictory geometry SHALL withhold the affected envelope; a uniform buffer SHALL not substitute for distinct front, side and rear requirements.

#### Scenario: Supported envelope
- **WHEN** lot orientation and applicable setbacks are established
- **THEN** the map shows labeled edges and the computed region, the linked card explains the rule, and exported GeoJSON retains provenance and conditional status

#### Scenario: Irregular or empty envelope
- **WHEN** geometry is irregular, invalid, ambiguous or too small for a nonempty supported region
- **THEN** the system handles the geometry explicitly and does not display a misleading buildable polygon

### Requirement: Full-feature PRD acceptance
Release SHALL demonstrate every row of docs/prd-delivery-plan.md with linked evidence, including its six bonus features. Acceptance SHALL use at least twelve real parcels, six non-Louise holdouts and positive cases for all three project packages. Curated seeds, always-unsupported packages and passing unit tests alone SHALL not satisfy product acceptance.

#### Scenario: Clean holdout run
- **WHEN** generated observations and caches are cleared and six holdout parcels are searched
- **THEN** the general pipeline runs without per-address edits, at least five of six independently legible maps yield usable cited dimensions, and no accepted measurement has wrong identity, units or unsupported precision

#### Scenario: Complete integrated demonstration
- **WHEN** release is declared
- **THEN** the report includes scenario comparison, feedback, grounded follow-up, map linkage, geometry export, admin ingestion/review, responsive keyboard/mobile flows, recovery checks and the production architecture

#### Scenario: Missing gate or schedule
- **WHEN** a required feature, accuracy gate or timebox is unmet
- **THEN** release status names the failure and remaining work rather than treating task completion or synthetic examples as full PRD compliance


## MODIFIED Requirements

### Requirement: Deterministic supported evaluation
The system SHALL evaluate reviewed rules against identified parcel facts and explicitly attributed project inputs. For a fixed fact snapshot, project inputs, and rule-set version, the regulatory results SHALL be identical. Missing inputs SHALL not be guessed by an LLM or silently replaced with defaults.

#### Scenario: Missing lot width
- **WHEN** a supported yard rule requires lot width and no accepted source-backed, verified or user-supplied width exists
- **THEN** that constraint needs review and identifies the missing input without inventing a yard value

#### Scenario: Updated project input
- **WHEN** the user changes a required input such as building height
- **THEN** dependent constraints are recomputed and the result identifies that input as user supplied


## MODIFIED Requirements

### Requirement: Constraint evidence and confidence
Each constraint SHALL expose evaluated, conditional, needs-review, or unsupported status; value and units when evaluated; input provenance; rule and source versions; passage citations; derivation; and high, medium, conditional, or undetermined confidence with reasons. Confidence SHALL describe evidence quality, not a probability of permit approval.

#### Scenario: Reviewed calculation with supplied dimensions
- **WHEN** all applicability predicates are established but a calculation uses a user-supplied dimension
- **THEN** the result shows that dimension and its provenance, the calculation, and medium confidence with the reason

#### Scenario: Evidence complete for supported scope
- **WHEN** the approved rule's inputs and applicability are established by verified evidence
- **THEN** the evaluated result has high confidence within its stated scope and retains explicit coverage limits


## MODIFIED Requirements

### Requirement: Actionable constraint blockers
Every unevaluated constraint SHALL display its primary blocker and next action without expanding details. Machine-readable blockers SHALL identify missing inputs, unresolved applicability, unavailable sources, conflicts, stale evidence or unsupported scope, and link to the relevant evidence or control. Unsupported results SHALL not suggest entering dimensions can make unsupported rules evaluable.

#### Scenario: Missing depth with available public evidence
- **WHEN** front-yard calculation is blocked and a map dimension observation exists
- **THEN** the card explains the remaining review need and links directly to that observation or its acceptance control instead of only showing a dash or internal field name

#### Scenario: Proposed design input
- **WHEN** side-yard or height calculation needs proposed building height or roof slope
- **THEN** the card names the project input and focuses its labeled control without implying that existing-building GIS supplies the proposed design

#### Scenario: Source failure versus unsupported scope
- **WHEN** a source fails or the selected project variant or zone is outside the reviewed packages
- **THEN** a source failure offers retry and identifies the source, while unsupported scope explains the coverage limit without a misleading retry or input-completion promise


## MODIFIED Requirements

### Requirement: Explicit evidence acceptance and calculation provenance
The system SHALL reuse reviewed observations or corroborated machine readings without transcription, with source and acceptance attribution. Machine corroboration and user acceptance SHALL remain distinct from legal verification. Conflicting, unvalidated or stale evidence SHALL not clear gates; unrelated applicability and confidence requirements SHALL remain binding.

#### Scenario: Accept sourced dimensions
- **WHEN** a user accepts current reviewed map measurements for a supported parcel and supplies the remaining necessary applicability basis and project inputs
- **THEN** dependent calculations use the selected measurements, retain their source links and acceptance attribution, and report medium confidence when relying on user assertions

#### Scenario: Map review is not legal verification
- **WHEN** an operator confirms the numbers on an assessor sheet but has not established legal lot applicability
- **THEN** the measurements are available without transcription, but the system does not label them independently verified legal dimensions or clear unrelated applicability checks

#### Scenario: Unresolved checks remain binding
- **WHEN** dimensions are available but frontage averaging, ordinary-lot conditions or other required evidence remain unresolved
- **THEN** dependent numeric answers remain withheld with the specific remaining checks visible

#### Scenario: Client claims verification
- **WHEN** a client submits a verification flag, reviewer identity or evidence reference not recognized by the server snapshot
- **THEN** it cannot create trusted evidence or obtain high-confidence output
