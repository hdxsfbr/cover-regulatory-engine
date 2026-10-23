# POC demonstration

Use [the current five-step validation demo](poc-validation.md) for measured outcomes, recorded limitations and reproducible commands.

Run the live backend/frontend as in README. Enter an address or APN that has never been added to code. Six frozen non-Louise examples are in `data/delivery/corpus.json`; the opt-in script `node frontend/scripts/live-acceptance.mjs` repeats the actual browser/source/model journey using the configured subscription.

1. Search an address, choose **Open assessment** on the matching parcel, and watch immediate loading and background document stages. Parcel/zoning/building evidence appears before map interpretation finishes. A failed source has a retry action and never turns into a recorded example.
2. Use **Inspect evidence** (or **Inspect map readings** when the job completes) to open public parcel evidence. Inspect an automatic map reading, its printed crop, full page and source link. Tract maps are discovered from legal identity. Irregular parcels may have a useful printed area while width/depth remain unresolved.
3. Select single-family, detached ADU or guest house in the property header. The map and assessment overview come first; compact constraint rows retain visible blockers and **Evidence & explanation** details. Use **Review next item** for a targeted action or **Edit project inputs** to open the input panel. Read the coverage summary and supply actual design/use choices. Conditional values retain their assumptions; unknown conditions never become evaluated numbers simply because the project type changed. Building-line evidence can leave the front yard conditional while independent constraints remain useful.
4. Open **Save / compare / ask** in the toolbar. Save a named scenario, change height/area/use, and save another. Compare both, reload the page, use **Open a saved project** on the search page, reopen the project and select a saved revision. Follow-up and feedback target that revision; save again to ask about a changed design.
5. Ask why a constraint is conditional. Expand the returned evidence citation. Suggested changes are text only; the question cannot silently change design inputs. Submit feedback against the assessment or a selected constraint.
6. For a rectangular lot with explicitly established document frontage, supply the relevant design inputs and inspect the setback envelope. Select a constraint's “Locate on map,” then select the edge to focus its card. Export GeoJSON and inspect CRS, units, rule/document versions and assumptions. A conditional envelope is labeled as such. An ambiguous/irregular parcel gets a specific withholding reason.
7. At `/operator`, inspect source passages and run extraction. Correct a candidate, record an attributed review, activate it and recalculate. Review feedback and inspect prior versions. Reactivating an eligible prior review performs rollback; stale-source or invalid versions are rejected.

Concrete positive examples:17404StaggSt and17413LemacSt have automatically read areas sufficient for the selected guest-house branch, with partial dimensional results because their shapes are irregular.7745LouiseAve has an automatically read rectangular map and a recorded building-line match: its front yard/envelope remains conditional rather than hiding the restriction. The ADU800sqft value is the selected state-exempt branch boundary, not a universal maximum.

Release artifacts, timings, source failures and the PRD matrix are in `docs/prd-release-report.md`. Recorded fixture mode remains useful for deterministic tests, and is visibly labeled; it is not evidence of live generalization.

### Design conflict and revision walkthrough
Open **PRD live acceptance — Stagg** from saved projects. The latest saved ADU design is restored automatically. Select **Detached ADU height 19**: the height row shows proposed 19 ft, limit 16 ft and an excess of 3 ft. The next action **Edit proposed height** opens and focuses that input. Change it to 15 ft to see the within-limit comparison.

Open **Save / compare / ask**. The selected saved assessment is named and unsaved changes are explicit. Questions and feedback are disabled until you save a new scenario or choose **Restore saved design**. Give revisions distinct scenario names before saving. The saved comparison shows each proposal and its outcome, while evidence versions remain inspectable. Map links only appear for actual category annotations; a withheld envelope is still explained.

### Progressive assessment while map reading runs

After choosing a live property, **Start with these findings** shows identified property, zoning status, map availability and preliminary constraint counts as soon as parcel context is available. **View available results** opens the current constraints; **Enter design while maps load** opens design inputs without waiting for extraction. Reader stages explain document discovery, page preparation, reading and validation without invented percentage estimates.

When the reader finishes, accepted measurements appear in the completion summary and dependent assessments refresh automatically. Your design entries remain. An empty reading explicitly says no usable dimensions were established; failure/cancel leaves the earlier facts and inputs available, with retry controls. Missing map documents and failed building sources are not presented as positive findings. This does not stream unvalidated model guesses or eliminate the initial parcel-source acquisition delay.

Browser regression: `cd frontend && npm test`. Live walkthrough: `node frontend/scripts/progressive-live.mjs` (17413 Lemac; public sources and subscription reader). For a cached property, completion may be immediate; controlled browser tests hold extraction open to verify all intermediate stages.
