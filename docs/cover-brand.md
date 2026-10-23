# Cover presentation

Reference: [Cover's public website](https://buildcover.com/), inspected 2026-10-22. OpenSpec change: `align-cover-brand`.

The UI uses the site's official symbol/wordmark, favicon and plus/close icon geometry, served locally under `frontend/public/brand/`. Source details are in that directory's README. The wordmark is darkened for the light header.

Shared colors are charcoal #202020, white, warm-gray #808076, a quiet #fafaf8 canvas and neutral borders. Editorial headings use a Georgia/Helvetica pairing inspired by the reference's mixed serif/sans headlines. Commercial/trial webfont files are not redistributed. Status colors remain distinct and textual; brand colors do not replace evaluated/review/error labels.

Native disclosure semantics, focus rings, responsive layouts, source evidence and saved-project workflows are preserved. No regulatory or acquisition logic changed.

Verification: production build; 31 Playwright regression tests; live saved-Stagg assessment inspection at 1440, 760 and 390 pixels; keyboard disclosure toggling; no horizontal overflow or JavaScript errors. Local identity assets also rendered with external network requests blocked. Screenshots and browser proof are under `data/delivery/cover-brand/`.
