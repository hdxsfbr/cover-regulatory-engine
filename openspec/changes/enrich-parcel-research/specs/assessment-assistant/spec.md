## ADDED Requirements

### Requirement: Saved supplemental research citations
Scenario Q&A SHALL use the supplemental records captured with that scenario, including source availability and coverage limits, and cite supporting evidence. New live research SHALL NOT silently rewrite an older scenario's evidence.

#### Scenario: Permit history question
- **WHEN** a saved scenario contains PRISM records and the user asks about permits
- **THEN** the answer can cite those records, distinguishes issued permits from final approval, and does not infer lawful construction from missing history

#### Scenario: Refreshed research
- **WHEN** research is refreshed after a scenario was saved
- **THEN** the old scenario keeps its saved research and a newly saved scenario captures the refreshed evidence
