# Supplemental property research

OpenSpec change: `enrich-parcel-research`. Access investigated on 2026-10-22 before implementation. No service credentials are required by the verified public endpoints.

## Verified access

| Source | Observed public interface | Association and useful output |
| --- | --- | --- |
| ZIMAS | `https://zimas.lacity.org/arcgis/rest/services/zm4/landbase/MapServer/105/query`, then `/zm4WS/GetProjectData?PIN=…&APN=&project=` | Exact APN/BPP match resolves City PINs. Profile APN is checked again. Profile entries include zoning, hazards, housing and case references. Supplying APN to GetProjectData restricts its returned tabs, so the adapter uses PIN and confirms APN in the full profile. |
| Planning | ZIMAS `processdatalink.aspx` redirects to `planning.lacity.gov/pdiscaseinfo/Search/…`; document API `/pdiscaseinfo/api/Service/GetPddData?caseNumbers=…` | Case detail fields, public document URLs from embedded JSON and approved document lists. A community-plan case is an area reference, not necessarily a site entitlement. Initial-submittal attachments are available through the source portal, not downloaded by this adapter. |
| PRISM | `https://prism.dbs.lacity.gov/api/search/assessor?book=…&page=…&parcel=…&offset=…&limit=50` | Permit identifiers, types, dates, source status, recorded address and available public PDFs. Stagg returned five records, including duplicate permit numbers with distinct record IDs, retained rather than guessed away. |
| NavigateLA | `https://maps.lacity.org/arcgis/rest/services/Core/…` | Easement lines, sewer easement polygons, nearby sewer pipes, street records and cadastral parcels. Geometry is filtered against the parcel, with 100-foot context for streets/sewers. Report URLs from `NLA_URL` resolve against NavigateLA; attributes preserve engineering plan references. |
| Metro | `https://api.metro.net/LACMTA/stops/all` and `/LACMTA_Rail/stops/all` | Separate public bus and rail GeoJSON stop lists, cached for 24 hours; three nearest candidates within one mile. This is Metro coverage, not every regional operator or a frequency assessment. |
| Walking routes | `https://valhalla1.openstreetmap.de/route`, pedestrian costing | Public Valhalla/OSM service; estimated route distance, minutes and directions. Compact JSON avoids the service's rejection of form-encoded spaces. Requests are serialized, spaced and cached. |

Official interface discovery used the public applications' JavaScript and published service metadata. [Valhalla documents its public demo and fair-use policy](https://valhalla.github.io/valhalla/start/introduction/). A dedicated routing provider is needed before substantial production traffic.

## Behavior and limits

Research appears after regulatory results, with an assessment navigation shortcut. Sources load independently. Expand a source for records, matching basis, retrieval time, limits and next action. Retry refreshes only that source. A failed source is never treated as no records. A completed retrieval does not mean all source documents were interpreted.

Source reads have an 18-second request timeout, 100-second total adapter budget, 8 MB response cap and redirect-host checks. PRISM is limited to 200 records, ZIMAS to four PINs and six case-detail lookups, and each case to 50 document links. Truncation is explicit. Engineering lists the status of all five checked layers. Source vintages are unknown where not provided; retrieval timestamps are not publication dates.

The walking origin is a GIS point inside the parcel, not a verified entrance. Distances do not establish statutory ADU parking or height eligibility. Permit history does not prove final inspection or lawful construction. Engineering screening does not establish title rights, sewer capacity or service availability. These integrations add evidence without automatically changing regulatory predicates.

## Persistence and API

`POST /api/research/{planning|permits|engineering|transit}` accepts `{snapshot_id, fresh?: boolean}`. Snapshot identity is server-owned. Responses include immutable research record IDs. Success is cached for 24 hours; incomplete/error results for 60 seconds; explicit refresh bypasses the cache. Concurrent identical requests share a bounded task. Recorded mode returns an explicit not-checked record without network requests.

Scenario saves accept `research_ids: {source: record_id}`. The server validates source, APN and parcel geometry identity and copies exactly those records into the immutable scenario. Map extraction never rewrites research. Research updates mark the design unsaved; Q&A uses the selected saved revision and can cite individual research records. Old scenarios remain readable.

## Validation

Parser tests use retained public Stagg responses under `data/sources/research-recorded/`; routing/failure tests use identified synthetic responses. Browser tests cover independent failure/retry, save/reopen, changed-evidence dirty state, mobile layout and late responses after a parcel switch. Live proof and screenshots are in `data/delivery/enriched-research/`.

Observed live browser results:
- **17404 Stagg, APN 2202004010:** 5 permit records (one downloadable permit); 6 planning case/ordinance references (two ordinance documents discovered); 2 mapped easement features and 2 nearby sewer pipes; shortest of three estimated Metro walks approximately 0.38 miles.
- **7745 Louise, APN 2202005003:** 11 permit records (two downloadable permits); 7 planning references, explicitly partial because case-detail discovery stops after six; no matched easement features in the two checked layers and one nearby sewer pipe; shortest of three estimated walks approximately 0.22 miles.
- Both workflows were exercised in Chromium: search, select, open all four cards, expand case references/walking directions, save, reload saved project and inspect mobile layout. No JavaScript errors or horizontal overflow occurred.
- Automated validation: 121 backend tests and 31 browser tests passed; production build and strict change validation passed. Follow-up compatibility checks also cover retaining older research IDs while refreshing individual sources.
- Final browser follow-up: refreshed bus/rail and engineering research, saved the revised scenario, and asked which permits were found and whether issuance establishes final approval. The response cited the saved PRISM records and preserved the distinction; see `cited-followup.json` and screenshot. The two Planning ordinance links and the HVAC permit link returned HTTP 200 `application/pdf` (see `document-access.json`).
