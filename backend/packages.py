"""Reviewed bounded project packages, with distinct use and applicability predicates."""

import math


def digest(value):
    from backend.rules import digest as rule_digest

    return rule_digest(value)


DESIGN_NUMBERS = {
    "proposed_area_sqft": (1, 10000),
    "bedrooms": (0, 10),
    "stories": (1, 2),
    "existing_floor_area_sqft": (0, 100000),
}
DESIGN_CHECKS = {
    "existing_primary_dwelling": "An existing single-family dwelling is on this lot.",
    "new_detached": "This proposal is new detached construction, not an attached unit or conversion.",
    "has_kitchen": "The proposed unit includes kitchen facilities.",
    "rented": "The proposed unit will be rented or used as a separate dwelling.",
    "temporary_guests": "The unit is solely for temporary guests of the main dwelling occupants.",
    "near_transit": "The lot is within one-half mile walking distance of a qualifying major transit stop or high-quality transit corridor.",
    "roof_matches_primary": "The ADU roof pitch matches the primary dwelling.",
    "coastal_requirements_resolved": "Applicable Coastal Act requirements have been resolved.",
    "accessory_location_reviewed": "Accessory building location, alley clearance, passageway and separation have been checked against the cited provisions.",
}


def source(section):
    import json
    from backend.rules import ROOT, source_records
    from backend.reviewed import current_sources

    pins = json.loads((ROOT / "data/rules/package-source-pins.json").read_text())
    current = current_sources()
    if current.get(section) != pins.get(section):
        raise ValueError("Project package source has changed; operator review required")
    return source_records()[pins[section]]


def citation(section, start, end=None):
    s = source(section)
    a = s["text"].index(start)
    b = s["text"].index(end, a) if end else len(s["text"])
    return {
        "section": section,
        "url": s["url"],
        "quote": s["text"][a:b],
        "source_hash": s["content_hash"],
    }


def assess_accessory(context, project_type, inputs, checks, note):
    for k, v in inputs.items():
        if type(v) not in (int, float) or not math.isfinite(v):
            raise ValueError("Invalid numeric project input")

    from backend.facts import derive

    sourced_facts = derive(context)
    if (
        "existing_primary_dwelling" not in checks
        and sourced_facts["existing_primary_dwelling"]["state"] == "true"
    ):
        checks = {**checks, "existing_primary_dwelling": True}

    def c(key):
        return checks.get(key) is True

    scope_citations = []
    machine = {o["key"]: o for o in context.get("machine_observations", [])}

    def result(category, value, units, quotes, assumptions, derivation):
        return {
            "category": category,
            "status": "conditional" if assumptions else "evaluated",
            "value": None if assumptions else value,
            "units": units,
            "confidence": "conditional" if assumptions else "medium",
            "reasons": assumptions
            or [
                "Reviewed source interpretation with attributed project inputs; no permit determination."
            ],
            "citations": [*quotes, *scope_citations],
            "inputs": {
                k: {
                    "value": v,
                    "origin": "machine-corroborated"
                    if k in machine and machine[k]["value"] == v
                    else "project-input",
                    "evidence": machine[k]["reason"]
                    if k in machine and machine[k]["value"] == v
                    else note or "Design assumption",
                    **(
                        {
                            "document_hash": machine[k]["document_hash"],
                            "source_url": machine[k]["source_url"],
                            "page": machine[k]["page"],
                        }
                        if k in machine and machine[k]["value"] == v
                        else {}
                    ),
                }
                for k, v in inputs.items()
            },
            "derivation": derivation,
            "rule_version": digest([project_type, category, quotes])[:16],
            "blockers": [
                {
                    "code": "applicability",
                    "message": a,
                    "target": "input-panel",
                    "action": "review",
                    "label": "Review project facts",
                }
                for a in assumptions
            ],
            "conditional": {
                "value": value,
                "units": units,
                "label": "Conditional on the stated facts",
                "assumptions": assumptions,
                "derivation": derivation,
            }
            if assumptions and value is not None
            else None,
        }

    issues = []
    if context.get("jurisdiction") != "Los Angeles":
        issues.append("City of Los Angeles jurisdiction is not established")
    if context.get("regime") != "Chapter 1":
        issues.append("Chapter 1 applicability is not established")
    if context.get("zoning_status") != "resolved" or context.get("zone") not in (
        ("R1-1", "RS-1") if project_type == "adu" else ("R1-1",)
    ):
        issues.append(
            "This package requires a reviewed residential zoning designation; this designation is outside its coverage"
        )
    if not c("existing_primary_dwelling"):
        issues.append(
            "Existing single-family primary dwelling must be established; mapped footprints do not prove use"
        )
    if not c("new_detached"):
        issues.append("Package applies only to new detached construction")
    constraints = []
    if project_type == "adu":
        scope_citations.append(
            citation(
                "12.03", "ACCESSORY DWELLING UNIT (ADU).", "ACCESSORY LIVING QUARTERS."
            )
        )
        if context.get("zone") == "RS-1":
            scope_citations.append(citation("12.07.1", "1.", "2."))
        eligibility = citation(
            "HCD-ADU-2026",
            "   2. Single-Family Detached ADUs",
            "   3. Multifamily Converted ADUs",
        )
        precedence = citation(
            "HCD-ADU-2026",
            "HCD uses the term “66323 Units”",
            "The\nfour categories are:",
        )
        if not c("has_kitchen"):
            issues.append(
                "Independent living facilities including cooking must be proposed for an ADU"
            )
        if not c("coastal_requirements_resolved") and (
            "coastal_requirements_resolved" in checks
            or sourced_facts["Coastal Zone (state boundary)"]["state"] != "false"
        ):
            issues.append(
                "Coastal Act applicability is unresolved or positive; review the statewide boundary and required coastal approvals"
            )
        height_source = citation(
            "HCD-ADU-2026", "Height Requirements\nIs there a limit", "Attached ADUs\n"
        )
        height = (
            20
            if c("near_transit") and c("roof_matches_primary")
            else 18
            if c("near_transit")
            else 16
        )
        constraints = [
            result(
                "side-yard",
                4,
                "ft",
                [eligibility],
                issues,
                "State-exempt detached ADU side setback",
            ),
            result(
                "rear-yard",
                4,
                "ft",
                [eligibility],
                issues,
                "State-exempt detached ADU rear setback",
            ),
            result(
                "height",
                height,
                "ft",
                [eligibility, height_source],
                issues,
                "Selected state-exempt height allowance; transit and matching-roof branches require project evidence. This is not a claim that every larger local ADU is prohibited.",
            ),
            result(
                "floor-area",
                800,
                "sq ft",
                [eligibility],
                issues,
                "Maximum for this state-exempt branch; larger ADUs require the separate local-ordinance branch",
            ),
        ]
        notes = [
            "This package models Government Code 66323(a)(2) as explained by the March2026 HCD handbook. Front setback and lot coverage are not imposed on that state-exempt branch. Building code, health/safety, easements and Coastal Act obligations still apply."
        ]
        quotes = [precedence, eligibility]
    else:
        for name in context.get("checked_overlays", []):
            status = context["records"][name]["status"]
            if status != "no-match":
                issues.append(
                    f"{name}: {status}; guest-house applicability requires review"
                )
        definition = citation(
            "12.03",
            "An accessory building used solely as the temporary dwelling of guests",
            "(Added by Ord. No. 107,884",
        )
        eligibility = citation(
            "12.08",
            "7.\u00a0\u00a0\u00a0Accessory buildings",
            "8.\u00a0\u00a0\u00a0Accessory uses",
        )
        location = citation("12.21", "\u00a0\u00a0\u00a0(b)")
        if checks.get("has_kitchen") is not False or checks.get("rented") is not False:
            issues.append(
                "Explicitly confirm no kitchen and no rental or separate dwelling use"
            )
        if c("has_kitchen") or c("rented"):
            issues.append(
                "Proposed cooking/rental use conflicts with accessory living quarters; assess an ADU instead"
            )
        if not c("temporary_guests"):
            issues.append(
                "Use must be solely temporary guests of the main dwelling occupants"
            )
        if inputs.get("lot_area_sqft", 0) < 10000:
            issues.append(
                "R1 accessory living quarters require at least10,000 sq ft of documented lot area"
            )
        if not c("accessory_location_reviewed"):
            issues.append(
                "Review rear-half siting, alley clearance, building separation and passageway requirements"
            )
        if not c("ordinary_context"):
            issues.append(
                "Ordinary interior-lot conditions must apply; reversed corner/through lots require separate interpretation"
            )
        width = inputs.get("lot_width_ft")
        height = inputs.get("building_height_ft")
        depth = inputs.get("lot_depth_ft")
        constraints.append(
            result(
                "rear-yard",
                5,
                "ft",
                [location],
                issues,
                "Accessory living quarters rear-yard requirement",
            )
        )
        constraints.append(
            result(
                "separation",
                10,
                "ft",
                [location],
                issues,
                "Minimum separation from main building or accessory living quarters, before other passageway requirements",
            )
        )
        if width is not None and height is not None:
            side = (5 if width >= 50 else max(3, 0.1 * width)) + max(
                0, math.ceil((height - 18) / 10)
            )
            sidequote = citation("12.08", "Side Yards.", "Rear Yard.")
            constraints.append(
                result(
                    "side-yard",
                    side,
                    "ft",
                    [location, sidequote],
                    issues,
                    "Main-building side yard of the same height, incorporated by12.21C5(e)",
                )
            )
        else:
            constraints.append(
                result(
                    "side-yard",
                    None,
                    "ft",
                    [location],
                    issues + ["Lot width and proposed height are needed"],
                    "Main-building side yard of the same height",
                )
            )
        if depth is not None:
            constraints.append(
                result(
                    "front-yard",
                    min(depth / 2, 55),
                    "ft",
                    [location],
                    issues,
                    "Accessory building lies on rear half, but need not be more than55ft from front line",
                )
            )
        else:
            constraints.append(
                result(
                    "front-yard",
                    None,
                    "ft",
                    [location],
                    issues + ["Documented lot depth is needed"],
                    "Rear-half siting with55ft ceiling",
                )
            )
        notes = [
            "Guest house means accessory living quarters: no kitchen, no rental or separate dwelling, temporary guests only. R1 permits this use only on lots at least10,000sqft. Two-story cap is not a height-in-feet determination. Residential floor area includes accessory buildings subject to defined exemptions."
        ]
        quotes = [definition, eligibility, location]
    if (
        context.get("jurisdiction") == "outside-city"
        or context.get("regime") == "Chapter 1A"
    ):
        for r in constraints:
            r.update(status="unsupported", value=None, conditional=None)
    implications = []
    for r in constraints:
        proposal = (
            inputs.get("proposed_area_sqft")
            if r["category"] == "floor-area"
            else inputs.get("building_height_ft")
            if r["category"] == "height"
            else None
        )
        if proposal is not None and r["value"] is not None:
            implications.append(
                {
                    "category": r["category"],
                    "proposed": proposal,
                    "limit": r["value"],
                    "fits_selected_branch": proposal <= r["value"],
                }
            )
    return {
        "status": "evaluated"
        if all(r["value"] is not None for r in constraints)
        else "partial",
        "project_type": project_type,
        "coverage": "Selected new detached ADU state-exempt dimensional branch"
        if project_type == "adu"
        else "Selected R1 detached accessory living quarters use and location rules",
        "constraints": constraints,
        "summary": {
            "notes": notes,
            "issues": issues,
            "citations": quotes,
            "design_implications": implications,
            "sourced_facts": sourced_facts,
        },
        "rule_set_version": digest(quotes)[:16],
        "checked_sources": list(context.get("records", {})),
    }
