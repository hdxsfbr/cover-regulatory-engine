## Purpose

Give an authorized operator an inspectable interface for real source acquisition, candidate correction, reviewed activation and feedback resolution.

## ADDED Requirements

### Requirement: Inspectable ingestion workflow
The operator UI SHALL expose source versions, acquisition/extraction status, candidate versus current values, validation failures and exact supporting source locations. It SHALL invoke the actual ingestion workflow and retain model, prompt, source and run provenance rather than simulate progress.

#### Scenario: Extract and inspect
- **WHEN** the operator ingests a selected source
- **THEN** the UI shows the real job outcome and allows inspection of candidates, dependencies and cited passages or map regions

### Requirement: Controlled correction and activation
Only an authorized operator SHALL correct, reject, review or activate candidates. Activation SHALL enforce source freshness, schema validity, resolved scope/dependencies and attributed review. Previous versions and the action history SHALL remain available; user feedback alone SHALL not authorize activation.

#### Scenario: Correct candidate
- **WHEN** the operator corrects an extracted threshold or interpretation
- **THEN** the correction is recorded separately with its basis, revalidated and reviewed before any current assessment uses it

#### Scenario: Unauthorized or superseded activation
- **WHEN** an ordinary client attempts activation or a candidate references superseded sources
- **THEN** the action is rejected without changing the active rule bundle

#### Scenario: Prior version and feedback
- **WHEN** an operator investigates disputed output
- **THEN** the original assessment, feedback, rule and source versions can be inspected and any eligible rollback or replacement is an attributed action
