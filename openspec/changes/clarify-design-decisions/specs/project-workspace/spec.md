## ADDED Requirements

### Requirement: Explicit saved design restoration
Opening a project with saved scenarios SHALL restore its most recent scenario and identify the restored design. Projects without scenarios SHALL explicitly identify a new unsaved design.

#### Scenario: Reopen ADU project
- **WHEN** the latest saved scenario is an ADU
- **THEN** the workspace restores ADU type, inputs, checks and evidence references and identifies the selected design

### Requirement: Useful saved design comparisons
Saved scenario comparisons SHALL display their proposal quantities, limits and outcomes from the saved assessment alongside evidence-version information. Missing historical comparisons SHALL be identified without inventing results.

#### Scenario: Compare height alternatives
- **WHEN** saved designs propose 19 and 16 ft against a 16 ft limit
- **THEN** comparison visibly distinguishes the exceeded design from the within-limit design

### Requirement: Explicit revision targets
The workspace SHALL identify the selected saved assessment and warn when design inputs, type, checks, note or evidence differ. Follow-up and feedback submission SHALL be disabled until the user saves the changed revision or explicitly restores the saved design. Existing answers SHALL not appear to answer an edited design.

#### Scenario: Edit after restoring
- **WHEN** a user changes the restored height from 19 to 15 ft
- **THEN** the workspace identifies unsaved changes, names the saved target, and offers saving or restoring before follow-up or feedback

#### Scenario: Save edited design
- **WHEN** the user saves the changed design
- **THEN** follow-up and feedback target that new immutable scenario and the unsaved warning clears
