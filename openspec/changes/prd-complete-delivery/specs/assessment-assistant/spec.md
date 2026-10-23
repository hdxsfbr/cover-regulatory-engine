## Purpose

Answer parcel and project follow-up questions using inspectable evidence from the current assessment and its explicit coverage limits.

## ADDED Requirements

### Requirement: Evidence-grounded follow-up
The assistant SHALL answer using the selected assessment, project inputs and retrieved source evidence. Factual regulatory or parcel claims SHALL reference supporting passages or observations. Unsupported questions SHALL receive an explicit evidence limitation rather than invented facts, citations or legal certainty.

#### Scenario: Explain a constraint
- **WHEN** a user asks why a setback or project limit applies
- **THEN** the answer explains the relevant input, rule and assumption with clickable citations tied to that assessment version

#### Scenario: Missing evidence
- **WHEN** the requested conclusion cannot be supported by available evidence
- **THEN** the answer identifies what is missing and a relevant next step without presenting a speculative value as an established finding

### Requirement: Bounded isolated assistant requests
Follow-up requests SHALL have visible progress, cancellation and bounded failure handling. Retrieved documents SHALL remain untrusted data. The assistant SHALL not cross project boundaries, execute document instructions, alter project inputs or activate rules without an explicit permitted user action.

#### Scenario: Malicious source or unrelated project
- **WHEN** source text instructs the assistant to ignore its task or a response from another project arrives
- **THEN** those instructions or unrelated data do not affect the current answer or application state

#### Scenario: Suggested design change
- **WHEN** the assistant suggests a scenario change
- **THEN** it identifies the suggested inputs and leaves the current scenario unchanged until the user explicitly applies them
