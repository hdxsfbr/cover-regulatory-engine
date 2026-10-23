# Parcel map evidence workflow

Public assessor sheets are fetched using the parcel's `Assr_Map`, not guessed
address matches. `data/parcel-evidence/<sha256>.pdf` preserves downloaded bytes.
The current reviewed observations identify Tract 16180 Lots 108 and 111 (Louise),
50 ft wide and 120 ft deep. Their 6000 sq ft area is derived from the rectangle,
not printed on the sheet. The sheet stamp is 1985. Lot 107 is clipped and must
not inherit these dimensions. No subsequent-title or legal-lot review is claimed.

To add a transcription, render and inspect the actual PDF, then prepare a JSON
candidate using the fields in `data/parcel-evidence/observations.json` (omit `id`
and `review`). Identify the correct AIN, map, exact legal description, tract/lot,
page/location, hash, numeric value, units and extraction method. Include explicit
rectangle derivation for any derived area. Do not create observations for ambiguous
readings or copy dimensions from a different lot.

Run from the repository root:

```sh
.venv/bin/python -m backend.evidence /absolute/path/candidate.json --reviewer 'Your name — transcription review'
```

This validates the retained hash, identity and units, records a transcription-only
review and replaces that parcel/key's previous record. Review is local operator
work; the public API cannot create trusted records. The API binds selection to
its immutable snapshot. Refresh to load a new review revision. A changed PDF
makes older readings stale. Conflicting current observations cannot be selected.

Hillside Ordinance (`Special_Areas/6`) and Coastal Commission Permit Area
(`zma/zimas/1605`) are independent screening observations. Neither negative query
establishes the composite legal non-hillside/non-coastal predicate. Unknown
vintage and coverage are explicit. Positive, failed or malformed observations
block dependent ordinary-case calculations. Hillside Grading Area is a different
layer; CPD Building Lines is not integrated by this change.

Derived areas also require `dimensions_ft` with `lot_width_ft` and `lot_depth_ft`;
the product must equal the recorded area and match current reviewed dimension
observations. An `ambiguous: true` candidate is rejected. New observations are
reviewed through the same local command for any parcel; there is no general
automatic scan-reading claim. The separate `recorded/` supplements preserve actual
screening/document responses without rewriting the original failure fixtures.
