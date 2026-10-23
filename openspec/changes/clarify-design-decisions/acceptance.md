# Acceptance — 2026-10-22

All six review findings are addressed:
1. Current height/floor-area rows show the backend proposal comparison, including excess, alongside a separately labeled rule-evaluation badge.
2. An exceeded evaluated limit takes priority in the next-action control and focuses the relevant design input.
3. Saved cards show proposal/limit/outcome from their immutable saved assessment. Missing historical comparisons remain explicit.
4. Opening Stagg restores its latest saved ADU, including its inputs/checks/evidence, and names the saved design.
5. Map buttons require matching category annotations; withheld geometry keeps its explanation.
6. Edited type, dimensions, checks, note or evidence marks the revision unsaved. Follow-up/feedback are disabled, old answers hidden, and saving/restoring provides recovery.

Validation: frontend TypeScript/Vite production build; 25 Playwright browser tests including the new integrated six-issue workflow and existing SF/ADU/guest-house, recovery, evidence, map/export and feedback coverage; strict OpenSpec validation.

Live browser walkthrough used the actual Stagg saved project and both existing 19/16-foot ADU scenarios on localhost:5173. Verified automatic restoration, 3-foot excess, exact input focus, editing to15ft, disabled stale follow-up/feedback, restoring19ft, distinct saved outcomes, evidence navigation, no absent map links, no page errors, and no page overflow at390px. Existing user scenarios were not overwritten. Saving a new revision and reopening it were exercised against the isolated browser-test backend.

Screenshots and logs: `data/delivery/design-decisions/`. Visually inspected desktop conflict, revision warning/comparison and mobile results; widened comparison presentation and distinguished disabled buttons after inspection, then repeated browser checks.

Limit: this validates the application workflow, not professional acceptance or expanded regulatory coverage. No new model-generated follow-up answer was requested in the live walkthrough; targeting and submission availability were checked.
