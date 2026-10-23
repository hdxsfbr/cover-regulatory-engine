"""Versioned, finite rule evaluation; model output is never executable code."""

import hashlib
import json
import math
from backend.gis import ROOT
from backend import evidence as parcel_evidence

CATEGORIES = ("front-yard", "side-yard", "rear-yard", "height", "floor-area")
NUMBERS = {
    "lot_depth_ft": (1, 10000),
    "lot_width_ft": (1, 10000),
    "lot_area_sqft": (1, 10000000),
    "building_height_ft": (0, 200),
    "roof_slope_percent": (0, 200),
}
CHECKS = {
    "ordinary_context": "Conventional new main building on a legally established ordinary interior R1-1 lot (not a flag, through, or key lot); no special approvals, building lines, unit-development, public acquisition, or other exceptions apply.",
    "outside_hillside_coastal": "Evidence establishes that the property is outside Hillside Areas and Coastal Zones.",
    "frontage_reviewed": "Frontage averaging, key-lot and sloping-lot exceptions have been checked and do not supersede the ordinary front yard.",
    "side_conditions_reviewed": "The proposal is no more than two stories; side-wall plane breaks, rooftop decks and first-story garage exceptions do not affect the requested side yard.",
    "height_conditions_reviewed": "Block-height averaging, special height restrictions and terrain/roof-structure exceptions do not affect the ordinary height limit; the uppermost roof has a uniform slope across all portions.",
}


def source_records():
    return {
        d["content_hash"]: d
        for p in (ROOT / "data/sources/regulations").glob("*.json")
        for d in [json.loads(p.read_text())]
    }


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_rule(rule, sources):
    if not isinstance(rule, dict):
        raise ValueError("Rule must be an object")
    for key in (
        "id",
        "category",
        "operation",
        "zone",
        "units",
        "source_hash",
        "quote",
        "scope",
    ):
        if not isinstance(rule.get(key), str) or not rule[key].strip():
            raise ValueError(f"Invalid {key}")
    if type(rule.get("version")) is not int or rule["version"] < 1:
        raise ValueError("Invalid rule version")
    for key in (
        "exclusions",
        "required_checks",
        "required_inputs",
        "unresolved_references",
    ):
        if not isinstance(rule.get(key), list) or any(
            not isinstance(v, str) or not v for v in rule[key]
        ):
            raise ValueError(f"Invalid {key}")
    if not isinstance(rule.get("source_versions"), dict):
        raise ValueError("Missing applicability source versions")
    if (
        rule.get("category") not in CATEGORIES
        or rule.get("operation") != rule["category"]
    ):
        raise ValueError("Unsupported rule category/operation")
    if not rule.get("id") or not rule.get("version") or rule.get("zone") != "R1-1":
        raise ValueError("Missing rule identity or unsupported zone")
    source = sources.get(rule.get("source_hash"))
    if (
        not source
        or hashlib.sha256(source["text"].encode()).hexdigest() != source["content_hash"]
    ):
        raise ValueError("Missing or invalid source hash")
    if source["section"] != ("12.21.1" if rule["category"] == "height" else "12.08"):
        raise ValueError("Wrong primary section for category")
    if rule["source_versions"].get(source["section"]) != rule["source_hash"]:
        raise ValueError("Primary citation does not match pinned dependency")
    quote = rule.get("quote", "")
    if not quote or quote not in source["text"]:
        raise ValueError("Citation passage is absent from source")
    if rule.get("units") != ("sq ft" if rule["category"] == "floor-area" else "ft"):
        raise ValueError("Invalid rule units")
    if rule.get("unresolved_references"):
        raise ValueError("Unresolved rule references")
    if not rule.get("scope") or not rule.get("exclusions"):
        raise ValueError("Missing applicability scope or exclusions")
    if any(k not in CHECKS for k in rule.get("required_checks", [])) or not {
        "ordinary_context",
        "outside_hillside_coastal",
    } <= set(rule.get("required_checks", [])):
        raise ValueError("Invalid applicability predicates")
    extra = {
        "front-yard": "frontage_reviewed",
        "side-yard": "side_conditions_reviewed",
        "height": "height_conditions_reviewed",
    }.get(rule["category"])
    if extra and extra not in rule["required_checks"]:
        raise ValueError("Missing category applicability check")
    if set(rule.get("source_versions", {})) != {"12.03", "12.08", "12.21.1", "12.22"}:
        raise ValueError("Missing applicability source versions")
    for section, content_hash in rule["source_versions"].items():
        dependency = sources.get(content_hash)
        if (
            not dependency
            or dependency["section"] != section
            or hashlib.sha256(dependency["text"].encode()).hexdigest() != content_hash
        ):
            raise ValueError("Invalid dependency source")
    for citation in rule.get("supporting_citations", []):
        dependency = sources.get(citation.get("source_hash"))
        if (
            not dependency
            or rule["source_versions"].get(dependency["section"])
            != citation.get("source_hash")
            or not citation.get("quote")
            or citation["quote"] not in dependency["text"]
        ):
            raise ValueError("Invalid supporting citation")
    required = {
        "front-yard": ["lot_depth_ft"],
        "side-yard": ["lot_width_ft", "building_height_ft"],
        "rear-yard": [],
        "height": ["roof_slope_percent"],
        "floor-area": ["lot_area_sqft"],
    }[rule["category"]]
    if rule.get("required_inputs") != required:
        raise ValueError("Invalid required inputs")
    if "expression" in rule:
        from backend.expressions import evaluate

        defaults = {k: 100 for k in rule["required_inputs"]}
        if evaluate(rule["expression"], defaults)[1] != rule["units"]:
            raise ValueError("Expression unit mismatch")
    return rule


def load_rules():
    path = ROOT / "data/rules/active.json"
    if not path.exists():
        return [], "unavailable"
    bundle = json.loads(path.read_text())
    sources = source_records()
    current = json.loads((ROOT / "data/sources/current.json").read_text())
    for rule in bundle["rules"]:
        validate_rule(rule, sources)
        if (
            not rule.get("review", {}).get("reviewer")
            or not rule["review"].get("at")
            or rule["review"].get("digest")
            != digest({k: v for k, v in rule.items() if k != "review"})
        ):
            raise ValueError("Unreviewed or modified rule")
        if any(
            current.get(section) != h for section, h in rule["source_versions"].items()
        ):
            raise ValueError("Rule source is superseded; review required")
    if (
        set(r["category"] for r in bundle["rules"]) != set(CATEGORIES)
        or len(bundle["rules"]) != 5
    ):
        raise ValueError("Incomplete rule set")
    if bundle["version"] != digest(bundle["rules"])[:16]:
        raise ValueError("Invalid bundle version")
    return bundle["rules"], bundle["version"]


def calculate(category, values):
    if category == "front-yard":
        d = values["lot_depth_ft"]
        return min(0.2 * d, 20), f"min(0.20 × {d}, 20)"
    if category == "side-yard":
        w = values["lot_width_ft"]
        h = values["building_height_ft"]
        base = 5 if w >= 50 else max(3, w * 0.1)
        added = max(0, math.ceil((h - 18) / 10))
        return base + added, f"base {base} + ceil(max(0, {h} − 18) / 10)"
    if category == "rear-yard":
        return 15, "Ordinary main-building rear yard: 15 ft"
    if category == "height":
        slope = values["roof_slope_percent"]
        return (
            28 if slope < 25 else 33
        ), f"Roof slope {slope}%: 28 ft below 25%, otherwise 33 ft"
    if category == "floor-area":
        a = values["lot_area_sqft"]
        return (
            0.45 * a,
            f"0.45 × {a}; residential floor area across buildings, not footprint area",
        )
    raise ValueError("Unsupported operation")


def calculate_rule(rule, values):
    if "expression" not in rule:
        return calculate(rule["category"], values)
    from backend.expressions import evaluate

    value, unit = evaluate(rule["expression"], values)
    if unit != rule["units"]:
        raise ValueError("Rule result unit mismatch")
    from backend.expressions import describe

    return value, describe(rule["expression"])


def assess(
    context,
    project_type,
    inputs,
    checks,
    evidence_note="",
    bundle=None,
    observation_ids=(),
):
    from backend.facts import derive

    source_checks = {}
    facts = derive(context)
    fact = facts["outside_hillside_coastal"]
    if "outside_hillside_coastal" not in checks and fact["state"] == "true":
        source_checks["outside_hillside_coastal"] = fact
        checks = {**checks, "outside_hillside_coastal": True}
    selected = parcel_evidence.select(context, observation_ids, inputs)
    machine = {
        o["key"]: o
        for o in context.get("machine_observations", [])
        if o.get("status") == "machine-corroborated"
        and o.get("document_hash")
        in {
            context.get("document", {}).get("content_hash"),
            *(
                d.get("content_hash")
                for d in context.get("automatic_evidence", {}).get("documents", [])
            ),
        }
        and o["key"] not in inputs
        and o["key"] not in selected
    }
    inputs = {
        **{k: o["value"] for k, o in machine.items()},
        **inputs,
        **{k: o["value"] for k, o in selected.items()},
    }
    for key, value in inputs.items():
        if (
            key not in NUMBERS
            or isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not NUMBERS[key][0] <= value <= NUMBERS[key][1]
        ):
            raise ValueError(f"Invalid value or units for {key}")
    if any(k not in CHECKS or not isinstance(v, bool) for k, v in checks.items()):
        raise ValueError("Invalid applicability check")
    if bundle is None:
        from backend.reviewed import active

        reviewed = active(context, project_type, inputs, checks, evidence_note, machine)
        if reviewed is not None:
            return reviewed
    if project_type in ("adu", "guest-house") and bundle is None:
        from backend.packages import assess_accessory

        return assess_accessory(
            {**context, "machine_observations": list(machine.values())},
            project_type,
            inputs,
            checks,
            evidence_note,
        )
    try:
        rules, version = bundle if bundle is not None else load_rules()
    except (ValueError, OSError, KeyError, TypeError) as e:
        rules, version = [], "unavailable: " + str(e)
    sources = source_records()
    unsupported = (
        project_type != "single-family"
        or context.get("jurisdiction") == "outside-city"
        or context.get("regime") == "Chapter 1A"
    )
    positive_zones = [z for z in context.get("zone_matches", []) if z["area_sqft"] > 0]
    if positive_zones and all(z["regime"] == "Chapter 1A" for z in positive_zones):
        unsupported = True
    issues = []
    if context.get("jurisdiction") != "Los Angeles":
        issues.append("LA City jurisdiction not established")
    if context.get("zoning_status") != "resolved":
        issues.append("Zoning requires review")
    elif context.get("zone") != "R1-1":
        unsupported = True
        issues.append("Complete zoning designation is outside the reviewed R1-1 scope")
    for name in context.get("checked_overlays", []):
        status = context["records"][name]["status"]
        if status != "no-match":
            issues.append(f"{name}: {status}; applicability requires review")
    for name in parcel_evidence.SCREENING:
        record = context["records"].get(name)
        if record and record["status"] != "no-match":
            issues.append(f"{name}: {record['status']}; applicability requires review")
    verified = {
        k: v
        for k, v in context.get("verified_facts", {}).items()
        if v.get("evidence") and v.get("reviewer") and v.get("verified") is True
    }
    supplied_inputs = dict(inputs)
    supplied_checks = {k: v for k, v in checks.items() if k not in source_checks}
    inputs = {**{k: v["value"] for k, v in verified.items() if k in NUMBERS}, **inputs}
    checks = {**{k: v["value"] for k, v in verified.items() if k in CHECKS}, **checks}
    for key, value in inputs.items():
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not NUMBERS[key][0] <= value <= NUMBERS[key][1]
        ):
            raise ValueError(f"Invalid verified input: {key}")
    if any(not isinstance(v, bool) for v in checks.values()):
        raise ValueError("Invalid verified check")
    results = []
    for category in CATEGORIES:
        category_issues = list(issues)
        building_lines = context.get("records", {}).get("CPD Building Lines", {})
        if (
            category == "front-yard"
            and building_lines
            and building_lines.get("status") != "no-match"
        ):
            category_issues.append(
                f"CPD Building Lines: {building_lines.get('status')}; front-yard applicability requires review"
            )
        rule = next((r for r in rules if r["category"] == category), None)
        result = {
            "category": category,
            "status": "unsupported" if unsupported else "needs-review",
            "confidence": "undetermined",
            "value": None,
            "units": "sq ft" if category == "floor-area" else "ft",
            "reasons": category_issues,
            "citations": [],
            "inputs": {},
            "derivation": None,
            "rule_version": None,
        }
        if unsupported:
            result["reasons"].append(
                "This project type, jurisdiction or zoning regime is outside the supported calculation scope"
            )
        if rule:
            src = sources[rule["source_hash"]]
            result["citations"] = [
                {
                    "url": src["url"],
                    "section": src["section"],
                    "quote": rule["quote"],
                    "source_hash": src["content_hash"],
                }
            ]
            for citation in rule.get("supporting_citations", []):
                support = sources[citation["source_hash"]]
                result["citations"].append(
                    {"url": support["url"], "section": support["section"], **citation}
                )
            result["rule_version"] = rule["id"] + ":" + str(rule["version"])
            result["scope"] = rule["scope"]
            result["exclusions"] = rule["exclusions"]
            missing = [k for k in rule["required_inputs"] if k not in inputs] + [
                k for k in rule["required_checks"] if checks.get(k) is not True
            ]
            if missing:
                result["reasons"].append("Missing or unresolved: " + ", ".join(missing))
            user_keys = [k for k in rule["required_inputs"] if k in supplied_inputs] + [
                k for k in rule["required_checks"] if k in supplied_checks
            ]
            evidence_ok = not [
                k for k in user_keys if k not in selected and k not in machine
            ] or bool(evidence_note.strip())
            if not evidence_ok:
                result["reasons"].append(
                    "Provide the basis for supplied dimensions and applicability assertions"
                )
            result["inputs"] = {
                k: {
                    "value": inputs[k],
                    "units": "sq ft"
                    if k == "lot_area_sqft"
                    else "%"
                    if k == "roof_slope_percent"
                    else "ft",
                    "origin": "user-supplied" if k in supplied_inputs else "verified",
                    "evidence": evidence_note
                    if k in supplied_inputs
                    else verified[k]["evidence"],
                }
                for k in rule["required_inputs"]
                if k in inputs
            }
            if not unsupported and not category_issues and not missing and evidence_ok:
                value, derivation = calculate_rule(rule, inputs)
                result.update(
                    status="evaluated",
                    value=value,
                    derivation=derivation,
                    confidence="medium"
                    if user_keys or source_checks or machine
                    else "high",
                    reasons=[
                        "Uses user-supplied dimensions/applicability assertions; not independently verified."
                    ]
                    if user_keys
                    else [
                        "Reviewed rule and verified evidence within the stated scope."
                    ],
                )
        else:
            result["reasons"].append("No current reviewed rule is available")
        if (
            rule
            and not unsupported
            and all(k in inputs for k in rule["required_inputs"])
            and result["status"] != "evaluated"
        ):
            value, derivation = calculate_rule(rule, inputs)
            assumptions = [
                CHECKS[k] for k in rule["required_checks"] if checks.get(k) is not True
            ]
            result["conditional"] = {
                "value": value,
                "units": result["units"],
                "derivation": derivation,
                "assumptions": assumptions + list(issues),
                "label": "Conditional scenario — applicability unresolved",
            }
        for key, observation in machine.items():
            if key in result["inputs"]:
                result["inputs"][key].update(
                    origin="machine-corroborated",
                    evidence=observation["reason"],
                    source_url=observation["source_url"],
                    document_hash=observation["document_hash"],
                    observation_id=observation["id"],
                )
        if category == "floor-area":
            result["additional_constraint"] = (
                "The 20-foot encroachment-plane origin and other massing requirements are not evaluated by this scalar floor-area cap."
            )
        for key, observation in selected.items():
            if key in result["inputs"]:
                result["inputs"][key].update(
                    origin="document-accepted",
                    evidence=f"User accepted map measurement; transcription reviewed by {observation['review']['reviewer']}. {observation['location']}",
                    source_url=observation["source_url"],
                    document_hash=observation["document_hash"],
                    observation_id=observation["id"],
                )
        result["blockers"] = blockers(
            context,
            result,
            rule,
            inputs,
            checks,
            unsupported,
            issues,
            evidence_note,
            supplied_inputs,
            supplied_checks,
            selected,
        )
        results.append(result)
    return {
        "status": "unsupported"
        if unsupported
        else (
            "evaluated"
            if all(r["status"] == "evaluated" for r in results)
            else "partial"
        ),
        "rule_set_version": version,
        "constraints": results,
        "project_type": project_type,
        "coverage": "Five ordinary-case Chapter 1 R1-1 scalar constraints only. Not a full buildability or permit determination.",
        "checked_sources": list(context["records"]),
        "applicability_assertions": checks,
        "applicability_evidence": {
            k: {
                "value": v,
                "origin": "user-supplied"
                if k in supplied_checks
                else "source-backed-inference"
                if k in source_checks
                else "verified",
                "evidence": evidence_note
                if k in supplied_checks
                else source_checks[k]["evidence"]
                if k in source_checks
                else verified[k]["evidence"],
            }
            for k, v in checks.items()
        },
        "evidence_note": evidence_note,
    }


INPUT_LABELS = {
    "lot_depth_ft": "legal lot depth",
    "lot_width_ft": "legal lot width",
    "lot_area_sqft": "legal lot area",
    "building_height_ft": "proposed building height",
    "roof_slope_percent": "proposed uppermost roof slope",
}
CHECK_LABELS = {
    "ordinary_context": "Confirm ordinary interior-lot conditions and review special approvals or building lines.",
    "outside_hillside_coastal": "Establish non-hillside and non-coastal applicability; screening no-matches alone do not establish it.",
    "frontage_reviewed": "Review frontage averaging, key-lot and sloping-lot exceptions.",
    "side_conditions_reviewed": "Review the proposed wall planes, rooftop decks and garage exceptions.",
    "height_conditions_reviewed": "Review block-height restrictions, terrain exceptions and uniform uppermost roof slope.",
}


def blockers(
    context,
    result,
    rule,
    inputs,
    checks,
    unsupported,
    issues,
    note,
    supplied_inputs,
    supplied_checks,
    selected,
):
    def item(code, message, target, action, label):
        return dict(
            code=code, message=message, target=target, action=action, label=label
        )

    if result["status"] == "evaluated":
        return []
    if unsupported:
        return [
            item(
                "unsupported",
                "This project type, jurisdiction or zoning is outside the supported R1-1 single-family rules.",
                "coverage",
                "review",
                "View supported scope",
            )
        ]
    output = []
    for issue in issues:
        failed = any(x in issue for x in ("unavailable", "not-checked"))
        output.append(
            item(
                "source-unavailable" if failed else "applicability",
                issue,
                "refresh-sources" if failed else "source-evidence",
                "retry" if failed else "review",
                "Retry parcel sources" if failed else "Inspect source evidence",
            )
        )
    if not rule:
        output.append(
            item(
                "rule-unavailable",
                "No current reviewed rule is available; rule review is required.",
                "coverage",
                "review",
                "View supported scope",
            )
        )
        return output
    for key in rule["required_inputs"]:
        if key in inputs:
            continue
        observed = [o for o in context.get("observations", []) if o["key"] == key]
        doc = context.get("document", {})
        if observed:
            status = observed[0]["status"]
            output.append(
                item(
                    "document-review" if status == "reviewed" else status,
                    f"Review the sourced {INPUT_LABELS[key]} and accept it for this assessment."
                    if status == "reviewed"
                    else f"The {INPUT_LABELS[key]} evidence is {status}; resolve it before use.",
                    "parcel-evidence",
                    "review",
                    "Review map evidence",
                )
            )
        elif key in parcel_evidence.BOUNDS and doc.get("status") == "unavailable":
            output.append(
                item(
                    "source-unavailable",
                    f"The assessor map for {INPUT_LABELS[key]} could not be retrieved.",
                    "refresh-sources",
                    "retry",
                    "Retry parcel sources",
                )
            )
        else:
            output.append(
                item(
                    "missing-input",
                    f"Supply {INPUT_LABELS[key]} and its basis."
                    + (
                        " A public map is available for review."
                        if doc.get("status") == "available"
                        and key in parcel_evidence.BOUNDS
                        else ""
                    ),
                    "input-" + key,
                    "input",
                    "Enter " + INPUT_LABELS[key],
                )
            )
    for key in rule["required_checks"]:
        if checks.get(key) is not True:
            output.append(
                item(
                    "applicability",
                    CHECK_LABELS[key],
                    "check-" + key,
                    "review",
                    "Review this condition",
                )
            )
    if not note.strip() and (
        any(k in supplied_inputs and k not in selected for k in rule["required_inputs"])
        or any(k in supplied_checks for k in rule["required_checks"])
    ):
        output.append(
            item(
                "missing-basis",
                "Describe the basis for your project inputs and applicability assertions.",
                "evidence-note",
                "input",
                "Add evidence basis",
            )
        )
    return output


from backend.packages import DESIGN_NUMBERS, DESIGN_CHECKS

NUMBERS.update(DESIGN_NUMBERS)
CHECKS.update(DESIGN_CHECKS)
