# Project package coverage and review

Source review: 2026-10-22. This is an agent passage/implementation comparison, not independent professional validation. Hash pins are in `data/rules/package-source-pins.json`; changing a source invalidates the built-in accessory package until review. Operator-reviewed expression packages have their own immutable review/activation records.

| Package | Primary evidence | Implemented branches | Remaining dependencies / exclusions |
|---|---|---|---|
| Single-family main building | LAMC12.03,12.08,12.21.1,12.22, publisher2026Rev9 | Ordinary Chapter1 R1-1 front/side/rear yards, roof-sensitive height, aggregate residential floor-area ratio; finite typed expressions | Frontage averaging, building lines, special approvals, terrain/roof exceptions, encroachment planes and wider code coverage remain explicit checks |
| New detached ADU | Official HCD March2026 ADU Handbook, pp16,24, discussing Gov.Code66323(a)(2),66321(b)(4) | Existing single-family primary, new detached construction, independent cooking; state-exempt800sqft branch,4ft side/rear,16/18/20ft selected height branches | Local ordinance/larger units, attached/conversion/JADU/multifamily branches not evaluated. State-exempt allowance is not a universal maximum. Building/health/safety/Coastal Act obligations remain. Direct statute retrieval returned403; handbook is primary agency guidance, not a substitute claim of direct statute verification |
| Guest house/accessory living quarters | LAMC12.03 definition;12.08A7 eligibility;12.21C5(b–g) location;12.08 side-yard cross-reference | Temporary guests only, explicitly no kitchen/no rental;10,000sqft lot minimum; rear5ft; main-building side yard of same height; rear-half/55ft siting;10ft separation | Reversed corners/through lots, alley centerline clearance, passageways, height-in-feet and floor-area exemptions require additional resolution. Not an ADU alias |

No APN-specific condition establishes a legal fact. The package scope is deliberately bounded; other zones and Chapter1A retain their context and are not promoted to a covered package. A conditional number carries assumptions separately from its evaluated value.

The guest-house provision explains why a6,000sqft Louise lot cannot be used as a positive guest-house example. Synthetic10,000/15,000sqft rule-boundary tests are labeled synthetic; real positive parcel validation is still required by the release plan.

## Applicability and precedence matrix

As-of review is2026-10-22. Publisher revision/retrieval timestamps are source metadata, not invented effective dates. Unknown legal effective dates remain unknown; optional rule validity intervals are checked on activation. A historical source snapshot is never silently relabeled current after a failed fetch.

| Fact | Acquisition / state | Effect |
|---|---|---|
| Jurisdiction, zoning regime and complete designation | County city boundary and City Chapter1/1A intersections; resolved/ambiguous/unavailable | Main building and guest-house require R1-1; the selected ADU branch supports R1-1 and RS-1. Chapter1A never inherits Chapter1 |
| Existing primary dwelling | County residential/single-use and one-unit attributes | Automatically supplies source-reported eligibility, with the limitation that assessor use is not current occupancy/permit proof |
| Hillside | City Hillside Ordinance layer | Positive or unavailable status prevents an unconditional ordinary main-building result |
| Coastal | Statewide Coastal Commission conformed boundary served by Caltrans, with100ft proximity margin | No-match can support outside-coastal inference; positive/unknown needs review. The older City permit-area layer alone does not establish the statewide boundary |
| Building line | CPD Building Lines, including ordinance/case/setback attributes | Positive/unavailable checked record blocks ordinary main-building evaluation; absence describes this dataset only |
| Width/depth/area | Assessor and County recorded tract maps, model reading and GIS corroboration | Document/page/crop provenance; irregular width/depth withheld; printed area can remain useful |
| Neighbor averaging, special approvals, legal lot/frontage interpretation | Not comprehensively established by available GIS | Targeted professional assertions remain necessary; source viewer retains the provisions for inspection |
| Proposed use, cooking, rental, temporary guests, height/roof | Architect design inputs | Different package classification and constraint branches; unknown does not mean false |

The ADU branch uses the state-exempt allowance described by HCD, rather than importing ordinary main-building setbacks or floor-area ratios. The800sqft result is the selected branch boundary, not a citywide maximum. RS guest-house rules are not covered: the inspected12.07.1 source has a different15,000sqft eligibility threshold and is not silently treated as R1.

Real additional positive cases include17404StaggSt (printed10,720sqft) and17413LemacSt (printed10,400sqft). Their irregular shapes withhold scalar front/side calculations, while the guest-house rear/separation rules can give meaningful partial answers under the stated use/location assumptions. They are additions to the corpus, not replacements for failed holdouts.
