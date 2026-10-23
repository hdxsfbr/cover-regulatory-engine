"""Source reports stay distinct from legal verification and project assertions."""

from backend import evidence


def derive(context):
    p = context.get("parcel", {})
    record = context.get("records", {}).get("Parcels", {})
    units = [p.get(f"Units{i}") for i in range(1, 6)]
    primary = (
        p.get("UseType") == "Residential"
        and p.get("UseDescription") == "Single"
        and units[0] == 1
        and all(u in (None, 0) for u in units[1:])
    )
    output = {
        "existing_primary_dwelling": {
            "state": "true" if primary else "unknown",
            "value": True if primary else None,
            "tier": "source-reported",
            "evidence": f"County assessor use: {p.get('UseType')}/{p.get('UseDescription')}; building unit counts: {units}",
            "source_url": record.get("source_url"),
            "retrieved_at": record.get("retrieved_at"),
            "limitation": "Assessor classification is not proof of current occupancy or permitted use.",
        }
    }
    designations = {
        z.get("zone") or z.get("designation")
        for z in context.get("zone_matches", [])
        if z.get("area_sqft", 0) > 0
    }
    output["resolved_zoning"] = {
        "state": "true"
        if context.get("zoning_status") == "resolved"
        else "conflict"
        if len(designations) > 1
        else "unknown",
        "value": context.get("zone"),
        "tier": "source-reported",
        "evidence": "Complete designation from intersected Chapter1/Chapter1A zoning polygons; multiple positive designations remain a conflict.",
        "sources": [
            r.get("source_url")
            for n, r in context.get("records", {}).items()
            if n in ("Chapter 1 zoning", "Chapter 1A zoning")
        ],
        "limitation": "A GIS designation does not resolve all parcel-specific ordinances or approvals.",
    }
    for name in (
        *evidence.SCREENING,
        "Coastal Zone (state boundary)",
        "CPD Building Lines",
    ):
        r = context.get("records", {}).get(name, {})
        output[name] = {
            "state": "true"
            if r.get("status") == "matched"
            else "false"
            if r.get("status") == "no-match"
            else "unknown",
            "tier": "source-reported",
            "source_url": r.get("source_url"),
            "evidence": r.get("status", "not-checked"),
            "limitation": "This predicate describes this named layer only; it does not establish every legal applicability condition.",
        }
    hillside = output["Hillside Ordinance"]
    coastal = output["Coastal Zone (state boundary)"]
    states = [hillside["state"], coastal["state"]]
    output["outside_hillside_coastal"] = {
        "state": "false"
        if "true" in states
        else "true"
        if states == ["false", "false"] and context.get("jurisdiction") == "Los Angeles"
        else "unknown",
        "value": False
        if "true" in states
        else True
        if states == ["false", "false"] and context.get("jurisdiction") == "Los Angeles"
        else None,
        "tier": "source-backed-inference",
        "evidence": "City Hillside Ordinance boundary and statewide Coastal Commission conformed boundary (100ft coastal query margin).",
        "sources": [hillside, coastal],
        "limitation": "Uses published mapped boundaries; conflicts and boundary proximity require review.",
    }
    return output
