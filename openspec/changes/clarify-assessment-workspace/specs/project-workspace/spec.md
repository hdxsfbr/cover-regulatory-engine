## ADDED Requirements

### Requirement: Discoverable secondary project tools
Saved projects, scenario saving/comparison, grounded follow-up and result-linked feedback SHALL remain reachable from workspace navigation without preceding the current property assessment. Opening or closing these tools SHALL preserve drafts, selected scenarios and question context. Saved-project opening SHALL also remain available before searching.

#### Scenario: Save and return to assessment
- **WHEN** a user opens project tools, edits a scenario name or question, closes them and returns
- **THEN** draft state remains and saving, comparison, feedback and cited follow-up retain their existing behavior

#### Scenario: Reopen a project
- **WHEN** a user opens saved-project tools before searching and chooses a project
- **THEN** its property and scenarios are restored, with historical evidence distinguished from current recalculation
