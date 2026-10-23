"""Design implications compare like quantities; they never claim permit feasibility."""


def summarize(assessment, inputs):
    constraints = assessment["constraints"]
    evaluated = sum(c["value"] is not None for c in constraints)
    conditional = sum(bool(c.get("conditional")) for c in constraints)
    implications = []
    for c in constraints:
        proposed = (
            inputs.get("building_height_ft")
            if c["category"] == "height"
            else inputs.get("proposed_area_sqft")
            if c["category"] == "floor-area"
            else None
        )
        if proposed is None:
            continue
        total = proposed
        if (
            c["category"] == "floor-area"
            and assessment["project_type"] == "single-family"
        ):
            if "existing_floor_area_sqft" not in inputs:
                implications.append(
                    {
                        "category": c["category"],
                        "message": "Supply existing counted residential floor area to compare the proposal with the aggregate cap.",
                        "status": "missing-input",
                    }
                )
                continue
            total += inputs["existing_floor_area_sqft"]
        limit = (
            c["value"]
            if c["value"] is not None
            else c.get("conditional", {}).get("value")
            if c.get("conditional")
            else None
        )
        if limit is not None:
            implications.append(
                {
                    "category": c["category"],
                    "message": f"Proposed quantity {total:g} {c['units']} {'is within' if total <= limit else 'exceeds'} the selected {limit:g} {c['units']} limit.",
                    "status": "conditional"
                    if c["value"] is None
                    else "within-limit"
                    if total <= limit
                    else "exceeds-limit",
                    "proposed": total,
                    "limit": limit,
                    "assumptions": c.get("conditional", {}).get("assumptions", [])
                    if c.get("conditional")
                    else [],
                }
            )
    issues = list(
        dict.fromkeys(
            reason for c in constraints if c["value"] is None for reason in c["reasons"]
        )
    )
    prior = assessment.get("summary", {})
    return {
        **prior,
        "headline": f"{evaluated} constraints evaluated; {conditional} conditional paths available.",
        "notes": prior.get("notes", [])
        + [
            "These comparisons cover the selected quantities; placement, construction-code compliance and permit eligibility are separate questions."
        ],
        "issues": issues,
        "design_implications": implications,
    }
