## ADDED Requirements

### Requirement: Actionable constraint blockers
Every unevaluated constraint SHALL display its primary blocker and next action without expanding details. Machine-readable blockers SHALL identify missing inputs, unresolved applicability, unavailable sources, conflicts, stale evidence or unsupported scope, and link to the relevant evidence or control. Unsupported results SHALL not suggest entering dimensions can make unsupported rules evaluable.

#### Scenario: Missing depth with available public evidence
- **WHEN** front-yard calculation is blocked and a map dimension observation exists
- **THEN** the card explains the remaining review need and links directly to that observation or its acceptance control instead of only showing a dash or internal field name

#### Scenario: Proposed design input
- **WHEN** side-yard or height calculation needs proposed building height or roof slope
- **THEN** the card names the project input and focuses its labeled control without implying that existing-building GIS supplies the proposed design

#### Scenario: Source failure versus unsupported scope
- **WHEN** a source fails or the selected project is an ADU, guest house or unsupported zone
- **THEN** a source failure offers retry and identifies the source, while unsupported scope explains the coverage limit without a misleading retry or input-completion promise

### Requirement: Explicit evidence acceptance and calculation provenance
The system SHALL allow reviewed document observations to supply dimensions without transcription, while separately establishing their applicability as legal inputs. User acceptance SHALL remain attributed and SHALL NOT become independent verification. Conflicting, unreviewed or stale evidence SHALL not clear a calculation gate. Existing deterministic calculations, confidence distinctions and scope gates SHALL remain intact.

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

### Requirement: Real-property usefulness acceptance
Acceptance SHALL compare before/after manual dimension entries and applicability checks for two supported Louise parcels, an irregular lot, Rhea ambiguity and an outside-city case. Both supported cases SHALL reuse source-backed dimensions without transcription. Each constraint SHALL have a traceable answer or an actionable visible blocker. Source inspection, browser checks and controlled failures SHALL be recorded separately from independent professional validation.

#### Scenario: Supported real-property walkthrough
- **WHEN** APNs 2202010006 and 2202010009 are exercised from lookup through evidence review and declared project input
- **THEN** their map measurements are already available, retained blockers are explicit, and evaluated results match documented source-based arithmetic with assumptions and provenance visible

#### Scenario: Failure and exclusion walkthrough
- **WHEN** an irregular parcel, Rhea zoning ambiguity, outside-city parcel, changed document, failed refresh or delayed source is exercised
- **THEN** the UI exposes the specific outcome without stale numbers, incorrect rectangular dimensions, invisible loading or hidden critical reasons

#### Scenario: Evidence does not establish complete applicability
- **WHEN** a walkthrough cannot establish a required legal condition from inspected evidence
- **THEN** acceptance records that unresolved condition rather than fabricating a positive real-world assessment or relabeling a hypothetical scenario as independent validation
