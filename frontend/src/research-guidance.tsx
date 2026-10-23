import type { Context } from "./main";

const needed: Record<string, string> = {
  ordinary_context:
    "Inspect the recorded lot layout, City zoning conditions, building lines and parcel-specific approvals. A clear GIS layer alone does not establish all exceptions.",
  frontage_reviewed:
    "Establish the front lot line from the recorded map and check neighboring front setbacks and any key-lot or slope exception.",
  side_conditions_reviewed:
    "Use the proposed elevations and floor plans to check stories, side-wall lengths, plane breaks, rooftop decks and garage exceptions.",
  height_conditions_reviewed:
    "Check proposed roof sections, grade information, neighboring heights and parcel-specific height restrictions.",
  outside_hillside_coastal:
    "Inspect the City Hillside and state Coastal boundary evidence; failed or boundary-adjacent queries need review.",
  existing_primary_dwelling:
    "Check the assessor use and unit count, then document any conflicting current or permitted-use evidence.",
  coastal_requirements_resolved:
    "Check the state Coastal boundary result and any required coastal approval; unknown is not outside.",
  accessory_location_reviewed:
    "Use the site plan and recorded map to establish rear-half placement, alley clearance, passageways and building separation.",
  near_transit:
    "Document the qualifying transit service and walking route; straight-line proximity alone does not establish this condition.",
};
export function ResearchGuidance({
  context,
  check,
  overridden,
}: {
  context: Context;
  check: string;
  overridden: boolean;
}) {
  const key =
    check === "coastal_requirements_resolved"
      ? "Coastal Zone (state boundary)"
      : check;
  const fact = context.sourced_facts?.[key];
  const resolved =
    fact &&
    (check === "coastal_requirements_resolved"
      ? fact.state === "false" && context.jurisdiction === "Los Angeles"
      : fact.state === "true");
  return (
    <small className="research-guidance">
      {resolved ? (
        <>
          <strong>
            {overridden
              ? "Source evidence (your override takes priority): "
              : "Automatically established for this calculation: "}
          </strong>
          {fact.evidence} {fact.limitation}
        </>
      ) : (
        needed[check] ||
        "Supply this choice from your proposed design; do not infer it from the parcel map."
      )}
      {fact?.source_url && (
        <>
          {" "}
          <a href={fact.source_url} target="_blank" rel="noreferrer">
            Inspect source ↗
          </a>
        </>
      )}
    </small>
  );
}
