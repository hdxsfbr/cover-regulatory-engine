# Applicability evidence acceptance — 2026-10-22

## Outcome

Both 7537 Louise (2202010006, Lot 108) and 7523 Louise (2202010009, Lot 111)
now expose their public assessor sheet, reviewed 50-foot width and 120-foot depth,
and separately derived 6000 sq ft area. The user can select each observation
without copying numbers. Page/lot, review attribution, document vintage and
source are retained. There is no claim of independent legal verification.

| Work per supported Louise parcel | Before | After |
| --- | ---: | ---: |
| Parcel dimension transcriptions | 3 | 0 |
| Explicit map-dimension acceptances | 0 | 3 |
| Proposed design numeric inputs | 2 | 2 |
| Applicability assertions | 5 | 5 |
| Basis note | 1 | 1 |

This reduces research/transcription; it does not eliminate legal review. Negative
hillside/coastal screening is shown but does not automatically clear the statutory
predicate. Unknown ordinary-lot, frontage, side-wall/deck and height exceptions
remain visible blockers. An unreviewed arbitrary map does not acquire dimensions.

## Source and calculation checks

The retained County PDF SHA-256 is
`1fb5359431e0aef739702af86d58362ade032b2f2f57cb169d23b0bd7c6f2e26`.
Its page was rendered and visually inspected, including the repeated dimensions
for Lot 111 and the clipped corner/different measurements on Lot 107. The map
is stamped 1985; no subsequent recorded changes were adjudicated. The review
records are transcription-only. Derived area validates 50 × 120 and its reviewed
width/depth dependencies. No measurements are hardcoded in the evaluator.

For the deliberately hypothetical ordinary design with 18 ft proposed height,
20% roof slope and explicitly assumed applicability, independent arithmetic from
the pinned rule passages is front min(0.2 × 120, 20) = 20 ft; side 5 ft with no
height increment; rear 15 ft; height 28 ft for slope below 25%; RFA 0.45 × 6000 =
2700 sq ft. Both real GIS contexts with accepted map dimensions produce those
values at medium confidence. This is a conditional design demonstration, not
independent real-project validation. The original 7537 zoning-timeout fixture is
unchanged; a separately retained successful live context tests the recovered case.

## Tests and browser observations

- 59 backend tests pass: PDF failure/content/size/redirect boundaries, total context
  deadline, identity/hash/unit/method checks, ambiguous readings, incorrect derived
  area, conflicting and stale observations, client-spoof rejection, legacy API,
  partial screening and positive/negative/unknown cases, snapshots and provenance.
- 18 browser tests pass on an isolated recorded backend (18081) and UI (5179):
  source acceptance with zero dimension transcription, keyboard action focus,
  unchanged/changed/failed refresh, user-input preservation, late responses,
  unsupported projects, malformed proxy responses and loading feedback.
- TypeScript/production build, unused/undefined-name checks and strict OpenSpec
  validation pass. The backend suite retains one existing Starlette/httpx
  deprecation warning.
- The actual live UI on port 5173 was walked from search through selection,
  evidence acceptance, project input and calculation for both Louise parcels.
  Selection-to-cards measured 1.009 seconds for cached 7537 and 11.620 seconds
  for uncached 7523. Separate fresh full-context requests with documents and
  screening measured 11.13 and 10.97 seconds respectively. These observations
  are not a future source-latency guarantee.
- A controlled HTTP 503 during refresh in the live browser removed numeric cards,
  disabled stale acceptance and retained the project note. Rhea then showed five
  visible blocker groups and zero evaluated results.
- Desktop and 390 px mobile screenshots were inspected: observation labels,
  measurement values, review status, checkboxes and source links are readable;
  no horizontal mobile overflow. Cards' actions open and focus the corresponding
  control. Actual screenshots and live walkthrough output are in
  [applicability-evidence/](applicability-evidence/).

Recorded cohort checks include the two positive contexts, irregular Lot 107,
Rhea ambiguity, Beverly Hills outside-city, Chapter 1A, positive Specific Plan,
and the original unavailable-zoning case. Single-family, ADU and guest-house
selections are covered; unsupported scope gets a coverage action rather than
misleading dimension-entry instructions.

## Reproduction

Run `.venv/bin/python -m pytest -q`, `npm --prefix frontend test`,
`npm --prefix frontend run build`, and
`openspec validate applicability-evidence --strict`. Browser tests no longer take
over the normal live backend's port. Follow docs/demo.md for the real UI path and
docs/parcel-evidence.md to review another source map. Existing snapshots remain
immutable; separate invalidation prevents document selections being reused after
known changed/unknown evidence. No automatic legal clearance or professional
validation is claimed by these checks.
