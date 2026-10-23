# Spec Delta

## Purpose

Give architects an interactive, evidence-backed assessment of supported residential constraints while making uncertainty and coverage limits inspectable.

## ADDED Requirements

### Requirement: Deterministic supported evaluation
The system SHALL evaluate reviewed rules against identified parcel facts and explicitly attributed project inputs. For a fixed fact snapshot, project inputs, and rule-set version, the regulatory results SHALL be identical. Missing inputs SHALL not be guessed by an LLM or silently replaced with defaults.

#### Scenario: Missing lot width
- **WHEN** a supported yard rule requires lot width and no verified or user-supplied width exists
- **THEN** that constraint needs review and identifies the missing input without inventing a yard value

#### Scenario: Updated project input
- **WHEN** the user changes a required input such as building height
- **THEN** dependent constraints are recomputed and the result identifies that input as user supplied

### Requirement: Constraint evidence and confidence
Each constraint SHALL expose evaluated, needs-review, or unsupported status; value and units when evaluated; input provenance; rule and source versions; passage citations; derivation; and high, medium, or undetermined confidence with reasons. Confidence SHALL describe evidence quality, not a probability of permit approval.

#### Scenario: Reviewed calculation with supplied dimensions
- **WHEN** all applicability predicates are established but a calculation uses a user-supplied dimension
- **THEN** the result shows that dimension and its provenance, the calculation, and medium confidence with the reason

#### Scenario: Evidence complete for supported scope
- **WHEN** the approved rule's inputs and applicability are established by verified evidence
- **THEN** the evaluated result has high confidence within its stated scope and retains explicit coverage limits

### Requirement: Applicability and coverage gates
The system SHALL withhold dependent calculations for ambiguous zoning, unknown applicability, or unmodeled conditions. Chapter 1A, ADU, guest-house, and other unsupported project types SHALL be labeled unsupported. Every assessment SHALL state its checked sources and supported scope without asserting overall legal buildability.

#### Scenario: Unsupported building type
- **WHEN** a user selects ADU or guest house
- **THEN** the parcel context remains visible and the system states that this building type's regulatory calculations are unsupported

#### Scenario: Overlay found
- **WHEN** a checked overlay applies but its effect is not modeled
- **THEN** affected constraints need review with the overlay identified and no unconditional numeric answer

#### Scenario: Unknown hillside applicability
- **WHEN** a rule requires a non-hillside parcel but that fact has not been established
- **THEN** the rule is withheld and the missing applicability evidence is reported

### Requirement: Inspectable interface
The interface SHALL provide address/APN entry, candidate selection, building-type selection, applicable input fields, a parcel/footprint map, and constraint details with citations. Facts, user inputs, calculations, and interpretations SHALL be distinguishable. Essential results and controls SHALL be usable by keyboard and available without relying on map colors.

#### Scenario: Inspect a result
- **WHEN** a user opens a constraint's details
- **THEN** its evidence, derivation, confidence reasons, and source links are available as text

#### Scenario: Context changes during lookup
- **WHEN** a user selects a new parcel while a previous lookup is pending
- **THEN** late responses from the previous lookup do not overwrite or combine with the new parcel's results

### Requirement: Bounded interactive responses
Assessment SHALL use preprocessed reviewed rules rather than live regulatory extraction. External lookup failures SHALL produce actionable partial or unavailable states within 30 seconds. Evaluation of already loaded facts and rules SHALL complete within one second at the 95th percentile over 100 runs on the documented development machine.

#### Scenario: Slow upstream source
- **WHEN** an upstream service does not respond within the lookup budget
- **THEN** the interface exits loading with a source-specific unavailable state and permits retry

### Requirement: Representative acceptance evidence
Acceptance SHALL include at least two independently checked supported R1 parcels, the recorded Rhea Court ambiguity case, a Chapter 1A case, an overlay case, an outside-city case, and missing-data/service-failure cases. Single-family, ADU, and guest-house selections SHALL be tested. Synthetic and recorded data SHALL be labeled; expected results SHALL not be generated solely by the evaluator under test.

#### Scenario: Reproducible acceptance run
- **WHEN** the recorded fixture suite runs without network access
- **THEN** supported numeric results match documented independent derivations and excluded cases produce their expected review or unsupported outcomes
