# Acceptance — 2026-10-22

Implemented all four tracked tasks. Existing backend request/response formats, regulatory packages and persistence are unchanged.

- 24 browser tests pass (30.6 seconds): original assessment, evidence, loading, recovery and workspace tests plus four new workflow tests. Updated selectors exercise intentional disclosures rather than bypassing them.
- New checks cover explicit keyboard candidate selection, DOM reading order, next-action focus, collapsed evidence/tools, retained drafts, all three project types at 390 pixels with no page overflow, background job cancel/retry, automatic map readings and crop access, readable blocker labels, bidirectional map linkage and conditional GeoJSON download.
- Frontend TypeScript/production build passes. Strict OpenSpec validation: 11 passed, 0 failed. Informational archive notices for older already-synced changes predate this change.
- Desktop and mobile screenshots inspected; retained at `data/delivery/ui-reorganization/desktop.png` and `mobile.png`. These use recorded/synthetic acceptance data, not a fresh regulatory assessment.
- Running live UI opened the existing Stagg project and rendered its property, map, constraints and background map-reading controls. This was a UI smoke check; it does not add independent regulatory verification.
- Demo instructions and opt-in live/geometry scripts now use the new evidence and project-tool disclosures. The full paid/public-service corpus was not rerun for this layout-only change.

The initial new job test expected exactly two HTTP starts; React development StrictMode starts the initial effect twice. It now verifies that retry adds one start relative to the observed baseline. One intermediate run overlapped a source edit and failed during hot reload; the final uninterrupted full run passes.

Professional usability testing remains outstanding. This change improves hierarchy and preserves functionality; it does not establish that architects have validated the design.
