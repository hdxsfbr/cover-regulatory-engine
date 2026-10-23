# Design

## Context
See proposal.md. The React App owns lookup/evaluation state; ProjectWorkspace owns persisted scenario and question state; EvidenceJob owns background polling. Existing tests select candidates explicitly and use section IDs for blocker navigation. The operator is a separate route.

## Goals / Non-Goals
Goals: change information hierarchy and presentation while preserving state, accessible targets, source provenance and recovery. Non-goals: backend/rule changes, new dependencies, invented completeness scores or professional approval claims.

## Decisions
- Reorder actual DOM sections, not only CSS: compact selected header and project selector, map/summary, constraint rows, input panel, source details, project tools. This keeps keyboard and reading order aligned.
- Keep explicit candidate selection with a clear action rather than automatically launching expensive research. Hide already-selected candidates; offer change-property navigation. Keep search accessible during pending/failed lookups.
- Use native details disclosures for evidence and project tools; keep their React components mounted to preserve drafts and jobs. Keep map-job progress outside the completed-reading disclosure. Reuse focusTarget to open containing disclosures and focus targets.
- Use compact semantic constraint articles with aligned columns and responsive stacking. Keep primary blocker/action visible; secondary blockers and complete citations remain in details. Retain conditional values as explicitly conditional, not established results.
- Expose next-step guidance from existing state and blockers, without new eligibility logic. Separate design inputs from professional assertions in copy; never encourage checking unknown legal facts to obtain numbers.
- Preserve existing IDs, source links and backend request shapes. Update browser selectors only where intentional labels/disclosures change, and add assertions for order, keyboard actions, state retention and mobile overflow.

## Risks / Trade-offs
- Collapsed sources could hide failures → keep job controls, primary blockers and source diagnostics visible.
- Moving conditional sections could reset child state → keep stable mounted project-tools disclosure and a single EvidenceJob instance.
- Compact rows can overflow long legal text → wrap cells and stack on mobile; visually inspect both layouts.
- In-page navigation can leave controls hidden → reuse ancestor-opening focus navigation and verify it by keyboard.

## Migration Plan
No data migration. Build and run existing browser regression suite plus new workflow checks; inspect representative fixture screenshots and live UI. Revert frontend layout changes if regressions remain; retain the original APIs and stored scenario format.
