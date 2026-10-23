# Recorded-map lot depth

Stagg inspection, 2026-10-22: **approximately 179.55 ft**, calculated from recorded boundaries rather than GIS scale. This is a source-derived Chapter 1 interpretation, not a current boundary survey or a City determination.

## Evidence and reasoning

17404 Stagg St is assessor parcel 2202-004-010, tract 15254 lot 10. The [County recorded tract map](https://pw.lacounty.gov/sur/nas/landrecords/tract/MB0369/TR0369-031.pdf), PDF page 3 / map book 369 page 33, identifies Stagg Street along the north frontage. It records a 171.10 ft west side and 188 ft east side. The west bearing is N00°01′39″W; the continuous east tract boundary is labeled NORTH. Frontage is 59.71 ft; the opposite southern boundary is 61.96 ft, along the shared rear boundary of adjoining lots. Dashed utility-easement lines are distinct from this boundary.

[LAMC 12.03](https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-108304) defines depth using the mean side-line direction. [City Planning ZI2391](https://zimas.lacity.org/zoneinfo/zi2391.pdf), PDF page 24 / technical-summary page 5, figures 3–4, illustrates the midpoint axis. [LADBS Zoning Manual](https://dbs.lacity.gov/sites/default/files/efs/pdf/publications/zoning/zoning-code-manual-and-commentary.pdf), PDF page 45 / printed page 31, explains how an opposite approximately parallel boundary can serve as the rear line, distinguishing it from triangular/gore cases using a 10-foot chord. These guidance documents are interpretive sources; they do not establish a parcel-specific approval.

For the identified opposite boundary and effectively parallel side lines, the mean-axis projection is `(171.10 + 188) / 2`, adjusted for the negligible bearing difference and rounded to **179.55 ft**. It is neither the longest side (188 ft), nor a depth obtained by dividing GIS area by frontage. The derived depth does not authorize treating the parcel as a rectangle or reconstructing a rectangular area/envelope.

## Qualifications that remain visible

- The rear-line classification is a source interpretation. Current legal lot-line applicability, later lot-line changes and special restrictions still require review.
- The recorded width is about 59.71 ft; the GIS front edge is about 64.28 ft. The recorded area is approximately 10,720 sq ft versus about 11,492 sq ft in GIS. The side lengths agree within the existing 4% corroboration tolerance, and reconstructed area is within 8%; the transverse discrepancy is explicitly reported. No legal width is inferred from GIS.
- Printed measurements/bearings have small closure differences; the supported derivation allows no more than 0.25 ft endpoint residual. The result is approximate.
- Professional ordinary-context and frontage assertions are not cleared by the reading. Irregular setback geometry remains withheld.

## General application behavior

The model reads identity, four boundary roles, printed lengths/bearings and page regions from the recorded tract map. Python calculates depth. The optional boundary extension applies to any qualifying LA Chapter 1 interior quadrilateral; there are no runtime APN/address exceptions or seeded Stagg observations.

Conservative automation limits: convex four-sided GIS shape without holes/multipart components; side bearings within 0.05 degrees, frontage perpendicular to the mean side direction within 1 degree, front/rear directions within 20 degrees, closure residual at most 0.25 ft, recorded side lengths/depth within 4% of corresponding GIS sides, and area within 8%. These thresholds bound implementation support; **they are not City legal definitions or survey tolerances**. Corner, through, curved, converging/gore, uncertain rear-line and conflicting source cases are rejected with a reason. Independently valid area readings survive a rejected depth.

The measurement retains raw operands, recorded document hashes/pages/crops, definition/guidance pins, method version and assumptions. A changed extraction prompt creates a different durable job cache key. Existing saved scenarios keep historical evidence; use **Refresh parcel sources** to run current extraction and save a new scenario afterward.

## Validation

Independent map inspection established the expected 179.55 ft before the model run. Tests cover Stagg, a rotated different-identity quadrilateral, malformed bearings/crops, conflicting measurements, excluded shapes/jurisdictions, source-pin changes, manual override provenance and unchanged applicability/geometry gates. Live extraction artifacts and browser proof are retained under `data/delivery/stagg-depth/`.
