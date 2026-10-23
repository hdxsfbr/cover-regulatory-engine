## Context
See proposal.md. The backend already supplies design_implications with proposed, limit, status and message. Main renders these only in the overview; saved cards omit them. Project opening resets type and inputs. Map actions are unconditional.

## Goals / Non-Goals
Goals: resolve the six observed workflow failures with shared presentation and existing endpoints.
Non-goals: new regulatory logic, expanded geometry, data migrations or changed immutable scenario semantics.

## Decisions
- Reuse backend comparisons in a shared component rather than duplicating regulatory calculations. Display excess only for an explicit exceeds-limit result.
- Prioritize exceeded results before generic blockers and focus the specific existing design input.
- Restore the latest returned scenario on project open; explicitly label restoration rather than silently resetting to single-family.
- Compare normalized current request fields with the selected saved request, including snapshot and observation IDs. Disable submission while different and hide prior answers. Offer restore and save actions rather than silently saving or asking about old data.
- Show map actions only for matching category features.

## Risks / Trade-offs
- Historical snapshots may lack comparisons → display unavailable comparison text; never infer old outcomes using current rules.
- Automatic evidence updates change snapshot → require save before questions so evidence versions remain explicit.
- Professional evidence status differs from design fit → preserve both labels with distinct wording.

## Migration Plan
Frontend-only, no database changes. Validate browser regression suite and live Stagg restoration/edit/comparison on desktop/mobile. Rollback frontend changes if needed; saved records remain compatible.
