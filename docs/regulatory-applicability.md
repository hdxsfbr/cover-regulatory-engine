# R1 applicability investigation

Status: source dependency analysis complete for the ordinary-case subset below. This matrix is not itself an active rule set; activation requires rule validation and explicit review. The four current published sections are preserved under `data/sources/regulations/`.

## Proposed narrow domain

Conventional single-family main-building projects in Chapter 1 with an unambiguous complete R1-1 designation. R1 variations, extra zoning conditions, Chapter 1A, ADUs, guest houses, special approvals, and unmodeled overlays are outside this initial calculation domain. An assessor parcel is not automatically a legally established zoning lot.

No-match results from the three configured overlays do not establish absence of subdivision conditions, variances, hillside/coastal restrictions, special height districts, or other exceptions. Every required fact must be independently evidenced or explicitly identified as a user assertion; unknown facts must withhold the affected calculation.

## Candidate calculation dependencies

| Category | Candidate ordinary-case relationship | Evidence required before application | Source and exceptions |
| --- | --- | --- | --- |
| Front yard | Lesser of 20% of legal lot depth and 20 feet, only if the averaging and special-lot provisions do not supersede it | Legal lot depth and frontage; developed-lot/front-yard evidence for the relevant frontage; key/corner/through-lot classification; relevant approvals | [12.08 C.1](https://codelibrary.amlegal.com/codes/los_angeles/latest/lapz/0-0-0-2052), [12.03](https://codelibrary.amlegal.com/codes/los_angeles/latest/lapz/0-0-0-886), and 12.22 C exceptions described below. A simple bounding-box depth is insufficient. |
| Side yards | Ordinary base is 5 feet per side; narrow-lot provision permits 10% of legal width with a 3-foot minimum | Legal lot width; stories; building height; new construction versus addition; hillside/coastal facts; wall geometry; roof-deck and approval conditions | 12.08 C.2(a)-(d): height-dependent increments for applicable non-hillside/non-coastal work, plane breaks, rooftop deck conditions, and precedence of subdivision/specific-plan/HPOZ requirements. Do not apply only the base width as a complete side-yard result. |
| Rear yard | Ordinary base is 15 feet | Legal rear-lot-line definition, lot configuration, project classification, and absence or handling of applicable exceptions/approvals | 12.08 C.3, 12.03 rear-line definition, and 12.22 C. The ordinary base cannot establish all allowed rear-yard encroachments. |
| Height | Ordinary non-hillside/non-coastal R1 limit is 33 feet, reduced to 28 feet for the specified low-slope uppermost roof condition | Roof slope by relevant portion; legal grade/height measurement; block-height evidence; hillside/coastal status; special districts and approvals; any claimed roof/terrain exception | [12.21.1 introductory provisions and B](https://codelibrary.amlegal.com/codes/los_angeles/latest/lapz/0-0-0-6325), 12.03 definitions. Roof slope threshold is 25%; block averaging and other exceptions must be checked. |
| Residential floor area | Ordinary non-hillside/non-coastal R1 cap is 0.45 times legal lot area | Legal lot area; hillside/coastal status; complete zone designation; approvals; residential-floor-area definition if comparing a proposed design | 12.08 C.5(a) and 12.03. Residential floor area is not synonymous with footprint area or assessor floor area. The accompanying encroachment-plane constraint remains relevant even when reporting this scalar cap. |

## Reviewed exception boundaries

The following branches are explicitly excluded from the first ordinary-case calculation, not treated as absent by default. Unknown or positive applicability yields needs-review for the affected constraint. A source-backed manual fact or a clearly attributed user assertion must establish the ordinary case.

| Provision | Supported handling | Required evidence/input |
| --- | --- | --- |
| 12.22 C.1 | No established building/setback line superseding the ordinary yard | Building-line/approval check |
| 12.22 C.2 | No first-story parking exemption claimed | Project description |
| 12.22 C.3, C.17-18, C.21, C.24-25, C.27-28 | Zone/project predicates exclude these non-R1 or alternative-development branches | Complete zone, conventional main-building project |
| 12.22 C.4-5, C.7, C.14-15, C.23 | Repealed or no provision in captured edition | Source snapshot |
| 12.22 C.6 | No sloping-lot front-yard reduction claimed; unknown terrain withheld | Elevation difference at the specified 50-foot point and curb level, or cited review |
| 12.22 C.8-9 | No unit-development or varying-side-yard arrangement | Frontage/deed/project evidence |
| 12.22 C.10 | Do not count half an alley toward R1 rear yard | R1 zoning predicate |
| 12.22 C.11-13 | No loading-space, accessory-yard, or public-acquisition exception claimed | Project and parcel history |
| 12.22 C.16 | Dwelling-density alley allowance is not an increase in legal lot area for residential-floor-area calculation | Keep density and area cap distinct |
| 12.22 C.19, C.22 | Through/flag/mountainous lot branches excluded | Interior ordinary-lot classification |
| 12.22 C.20 | Report main-wall setbacks only; projections and yard structures need separate review | No proposed projection/yard-structure assessment |
| 12.22 C.26 | Historic change-of-use branch excluded | New main-building project and historic-context check |
| 12.08 C.1 | Exclude frontage averaging and key-lot branches from ordinary formula | Frontage survey/review; not inferred from a building footprint |
| 12.08 C.2(a)-(d) | Base side yard plus the C.2(b) height increment for new non-hillside/non-coastal construction; no plane-break or roof-deck condition | Height, width, new-construction status; explicit wall-length/height and deck checks |
| 12.08 C.5(a) | Residential-floor-area cap only; report the 20-foot encroachment-plane origin as an additional unevaluated massing constraint | Legal lot area, non-hillside/non-coastal facts |
| 12.21.1 introductory text, A.9, B | Ordinary height limit with low-slope roof branch; special plans, districts, block averaging, terrain and roof-structure exceptions excluded | Roof slope, grade convention, district/approval and block checks |
| 12.03 | Use legal lot area/depth/width and the residential floor-area definition | User-entered or independently documented dimensions, never a bounding-box substitute |

For the supported new-construction side-yard branch, add one foot for each ten-foot increment or fraction above 18 feet to the base side yard. At or below 18 feet, add zero. For all categories, unresolved approvals, zoning conditions, missing predicate evidence, or source currency concerns must not be converted into an ordinary-case assumption.

The output describes five scalar constraint categories, not a complete massing envelope. The encroachment-plane caveat must remain visible alongside floor-area results. No geometry-generation capability is implied.

## Implemented evidence

The five rules are reviewed and active, with the original extraction and subsequent source-resolution record retained. See `docs/acceptance.md` for two real R1-1 GIS contexts and independently derived hypothetical design scenarios. Their scenario dimensions and applicability assertions are not verified site facts. Height calculations require uniform uppermost roof slope; mixed roof portions remain excluded and need separate analysis.
