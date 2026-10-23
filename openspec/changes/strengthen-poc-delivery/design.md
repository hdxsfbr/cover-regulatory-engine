## Context
Existing rules already derive limited source-backed applicability, but input controls do not explain this clearly. Job keys include retrieval time. Q&A omits saved parcel context. Existing cohort artifacts overstate outcome completeness.
## Goals / Non-Goals
Deliver all five priorities using existing APIs, fixtures and model adapter. No new legal rules, unconditional inferred ordinary-lot claims, or outside-review dependency.
## Decisions
- Cache by stable validation inputs and a UTC daily window. Include lot-depth derivation version and guidance pins; retain all existing provenance. A new day permits rereading supplemental sources. Geometry changes invalidate reuse instead of reusing geometry-correlated values.
- Display existing source deductions and evidence instructions beside checks rather than silently marking user assertions true. Preserve overrides and unknowns.
- Add bounded named evidence entries to question context, excluding full raw GIS feature arrays. Preserve exact quote validation and untrusted-source handling.
- Acceptance separates recorded-source replay from live browser checks and compares facts-only outcomes with explicitly hypothetical applicability scenarios. Report coverage and timing independently; do not turn partial results into pass counts.
## Risks / Trade-offs
Daily reuse can retain supplemental-map readings for the rest of a UTC day; provenance and freshness window stay explicit. Source-based facts are screening/inference, not complete legal adjudication. Public service failures remain in acceptance artifacts.
