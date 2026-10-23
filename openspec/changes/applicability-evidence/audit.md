# Real-property assessment audit — 2026-10-22

## Observed baseline

Read the primary project brief, current rules, GIS context builder, snapshot API, frontend cards/inputs, current specs, and acceptance reports. Queried the running live API with `fresh=true&compact=true`, then requested a single-family assessment with no supplied inputs. Exact observed summaries are retained in evidence/baseline-live.json; these are read-only live observations, not revised regression fixtures.

| AIN / property | Seconds, context + assessment | Result | User-facing consequence |
| --- | ---: | --- | --- |
| 2202010006 / 7537 Louise | 11.97 | R1-1 resolved; all eight sources successful | Five empty needs-review cards |
| 2202010009 / 7523 Louise | 13.11 | R1-1 resolved; all eight sources successful | Five empty needs-review cards |
| 2202010005 / 7543 Louise | 13.10 | Zoning needs review despite successful source responses | Zoning and missing-evidence blockers |
| 2126037055 / 6754 Rhea | 12.05 | Zoning needs review | Ambiguity plus missing-evidence blockers |
| 4328021043 / Beverly Hills condo | 11.01 | Outside City | Unsupported; response also includes irrelevant missing-input reasons |

Walked 7537 Louise through the running browser using address/APN entry, Find property and candidate selection. The five visible card texts contain only the title, needs-review badge, description, dash, undetermined confidence and collapsed evidence summary. Missing-input reasons and the entry controls require expanding separate details panels. Inspected the full-page screenshot: parcel/building outlines are visible; background tiles were not visible in this session. This audit does not establish a tile failure cause or change the optional tile policy.

Root causes:
- `backend/gis.py` does not supply `verified_facts`; the trusted-fact branch in `backend/rules.py` is exercised by synthetic tests, not live sourcing.
- Five numeric inputs (three parcel dimensions and two proposed design inputs) and five broad applicability checks are manual. A single free-text note attributes them all.
- Public map identity and legal-description fields are available but not used for document retrieval or dimension observations.
- Reasons already exist in the API, but only as free-form strings and are hidden in the UI. Unsupported cards retain distracting missing-input strings.
- No current test requires the default real-property flow to reduce user research or transcription.

## Inspected public evidence

### Assessor map: confirmed useful, scanned and dated

Downloaded the [official sheet 2202-010](https://maps.assessor.lacounty.gov/GeoCortex/Essentials/PAIS/REST/sites/PAIS/Resources/ParcelMap?MapId=2202-010-&f=file), HTTP 200, application/pdf, 53,178 bytes. Retained PDF and checksum/inspection record under evidence/. Rendered and visually inspected the entire sheet; text extraction does not expose the scanned measurements.

Lot 108/circled parcel 6 on Louise shows width 50 ft and depth 120 ft. Lot 111/circled parcel 9 repeats the standard row dimensions using ditto marks. 6000 sq ft is a rectangular derivation, not a printed area for these two lots. Lot 107/circled parcel 5 has a clipped corner, a 40-foot rear segment and different side lengths: it is a useful check against copying standard dimensions or rectangular area across the sheet. The sheet is stamped 1985 and references Tract 16180, M.B. 354-34-36. A current download is not proof that later recorded changes do not exist.

The [County tract-map search](https://pw.lacounty.gov/smpm/landrecords/TractMaps.aspx) is public and its search form was reached. The 16180 search attempted during this audit did not yield a captured direct PDF link. Recorded tract sheets and subsequent instruments were not inspected. Do not represent the assessor-map reading as a recorded-title or legal-lot review.

### Applicability screening: accessible observations, incomplete semantic evidence

Inspected metadata for:
- [Hillside Ordinance, Special_Areas/6](https://maps.lacity.org/lahub/rest/services/Special_Areas/MapServer/6): polygon layer, EPSG:3857; H_TYPE field. It is distinct from Hillside Grading Area layer 5.
- [Coastal Commission Permit Area, ZIMAS/1605](https://zimas.lacity.org/arcgis/rest/services/zma/zimas/MapServer/1605): polygon layer, EPSG:2229; NAME/CST_TYPE fields. Other coastal jurisdiction layers exist; this single layer must not be described as covering every coastal definition.
- [CPD Building Lines, City_Planning_Department/3](https://maps.lacity.org/lahub/rest/services/City_Planning_Department/MapServer/3): polyline layer with CASE_NUM, ORD_NUM, SETBACK and NLA_URL. Existing polygon-only helper cannot ingest it unchanged. Not selected for automatic legal clearance.

The first two were queried with the complete recorded Louise parcel polygon in EPSG:2229. Both returned no features and no transfer-limit flag; retained responses are in evidence/. These are fresh screening queries using recorded parcel geometry, separate from the running app's eight-source query. Metadata descriptions/copyright fields were empty and no adequate statutory coverage basis was established. They can reduce evidence discovery but cannot currently clear the composite non-hillside/coastal legal predicate.

### Inputs still requiring interpretation or proposed design

The pinned 12.03 text defines depth by front/rear lines and mean side-line direction, and width at mid-depth. A polygon's longest edge is not a general substitute. The assessor sheet helps this rectangular example but does not establish every exception. Existing front-yard averaging, special approvals, ordinary-lot and height-condition checks cannot be inferred from the three selected overlay no-matches. Proposed height and roof slope describe the user's project; historic building footprints are not those inputs.

## Change surface and acceptance measures

Backend: source manifest/queries, document retrieval and local evidence review, context snapshots and fingerprints, assessment request validation, provenance and structured blockers. Frontend: types, cards, evidence and input controls, focus behavior, loading/refresh state. Tests: document trust boundaries, scoped review, source conflicts, compatibility, representative recorded and live observations, keyboard/mobile browser flows. Docs: API, evidence review procedure, acceptance and roadmap. No external message, paid extraction or deployment is needed.

Before: each supported parcel requires three dimension transcriptions, two proposed design numeric inputs, five broad applicability assertions and a basis note. After required: zero dimension transcription for both Louise cases, explicit dimension acceptance, retained source attribution, and a measured count of remaining checks/project inputs. Do not count merely relabeled checkboxes as reduced verification. For all cohort cases, every card must expose a meaningful answer or blocker/action before expansion.

This audit is implementation planning evidence. It does not constitute independent project validation. Slow/failing/changed-source behavior will be exercised in the new change's controlled tests and browser acceptance rather than claimed from these successful live runs.
