"""Reviewed expression bundles can supersede a built-in project package."""

import json
from datetime import date
from backend import store, synthesis
from backend.expressions import evaluate, describe
from backend.rules import ROOT, CHECKS, source_records, digest


def current_sources():
    current = json.loads((ROOT / "data/sources/current.json").read_text())
    additional = ROOT / "data/sources/package-current.json"
    if additional.exists():
        current.update(json.loads(additional.read_text()))
    return current


def validate_activation(review):
    data = review["data"]
    if data["decision"] != "review" or data["candidate_digest"] != digest(
        data["candidate"]
    ):
        raise ValueError("Candidate is rejected or changed after review")
    sources = source_records()
    errors = synthesis.validate(data["candidate"], sources)
    if errors:
        raise ValueError(json.dumps(errors))
    rules = data["candidate"]["rules"]
    types = {r["project_type"] for r in rules}
    if len(types) != 1 or not types <= {"single-family", "adu", "guest-house"}:
        raise ValueError("Use one canonical project type per package")
    required = {
        "single-family": {
            "front-yard",
            "side-yard",
            "rear-yard",
            "height",
            "floor-area",
        },
        "adu": {"side-yard", "rear-yard", "height", "floor-area"},
        "guest-house": {"front-yard", "side-yard", "rear-yard", "separation"},
    }[next(iter(types))]
    if {r["category"] for r in rules} != required or len(rules) != len(required):
        raise ValueError("Incomplete or duplicate package categories")
    current = current_sources()
    for r in rules:
        if (
            r.get("valid_from") and date.fromisoformat(r["valid_from"]) > date.today()
        ) or (
            r.get("valid_until") and date.fromisoformat(r["valid_until"]) < date.today()
        ):
            raise ValueError("Rule is outside its reviewed validity interval")
        if (
            r.get("jurisdiction") != "Los Angeles"
            or r.get("regime") != "Chapter 1"
            or r.get("zone") != "R1-1"
        ):
            raise ValueError(
                "Activation requires explicit reviewed LA Chapter1 R1-1 scope"
            )
        checks = r.get("required_checks")
        if (
            not isinstance(checks, list)
            or not checks
            or any(k not in CHECKS for k in checks)
        ):
            raise ValueError(
                "Map applicability predicates to supported fact keys before activation"
            )
        for c in r["citations"]:
            src = sources[c["source_hash"]]
            if current.get(src["section"]) != src["content_hash"]:
                raise ValueError("Candidate source has been superseded")
    return next(iter(types))


def active(context, project_type, inputs, checks, evidence_note="", machine=None):
    machine = machine or {}
    activations = store.listing("rule-activation", project_type)
    if not activations:
        return None
    review = store.get(activations[0]["data"]["review_id"], "rule-review")
    # A superseded activated package fails closed; do not silently revive an older rule.
    validate_activation(review)
    candidate = review["data"]["candidate"]
    sources = source_records()
    # Preserve site eligibility and evidence even when an operator changes an expression.
    if project_type == "single-family":
        from backend.rules import assess, load_rules

        baseline = assess(
            context,
            project_type,
            {k: v for k, v in inputs.items() if k not in machine},
            checks,
            evidence_note,
            bundle=load_rules(),
        )
    else:
        from backend.packages import assess_accessory

        baseline = assess_accessory(
            context, project_type, inputs, checks, evidence_note
        )
    constraints = []
    for rule in candidate["rules"]:
        previous = next(
            (c for c in baseline["constraints"] if c["category"] == rule["category"]),
            {},
        )
        issues = (
            list(previous.get("reasons", [])) if previous.get("value") is None else []
        )
        if (
            context.get("jurisdiction") != rule["jurisdiction"]
            or context.get("regime") != rule["regime"]
            or context.get("zone") != rule["zone"]
        ):
            issues.append(
                "Parcel does not establish this reviewed jurisdiction/regime/zone"
            )
        issues += [
            CHECKS[k] for k in rule["required_checks"] if checks.get(k) is not True
        ]
        missing = [i["name"] for i in rule["inputs"] if i["name"] not in inputs]
        if missing:
            issues.append("Missing inputs: " + ", ".join(missing))
        value = None
        conditional = None
        if not missing:
            computed, unit = evaluate(rule["expression"], inputs)
            if unit != rule["units"]:
                raise ValueError("Rule result units changed")
            if issues:
                conditional = {
                    "value": computed,
                    "units": unit,
                    "assumptions": issues,
                    "derivation": describe(rule["expression"]),
                    "label": "Conditional reviewed expression",
                }
            else:
                value = computed
        constraints.append(
            {
                "category": rule["category"],
                "value": value,
                "units": rule["units"],
                "status": "needs-review" if issues else "evaluated",
                "confidence": "conditional" if issues else "medium",
                "reasons": issues
                or [
                    "Attributed reviewed rule; project assertions remain user supplied"
                ],
                "citations": [
                    {
                        **c,
                        "url": sources[c["source_hash"]]["url"],
                        "section": sources[c["source_hash"]]["section"],
                    }
                    for c in rule["citations"]
                ],
                "inputs": {
                    i["name"]: {
                        "value": inputs[i["name"]],
                        "origin": previous.get("inputs", {})
                        .get(i["name"], {})
                        .get("origin", "project-input"),
                        "evidence": previous.get("inputs", {})
                        .get(i["name"], {})
                        .get("evidence", "Current scenario input"),
                        **previous.get("inputs", {}).get(i["name"], {}),
                    }
                    for i in rule["inputs"]
                    if i["name"] in inputs
                },
                "derivation": describe(rule["expression"]),
                "rule_version": review["id"],
                "conditional": conditional,
                "blockers": [
                    {
                        "code": "applicability",
                        "message": message,
                        "target": "input-panel",
                        "action": "review",
                        "label": "Review project facts",
                    }
                    for message in issues
                ],
            }
        )
    return {
        "status": "evaluated"
        if all(r["value"] is not None for r in constraints)
        else "partial",
        "constraints": constraints,
        "coverage": "Operator-reviewed expression package; inspect applicability and exclusions",
        "project_type": project_type,
        "rule_set_version": review["id"],
        "checked_sources": list(context.get("records", {})),
    }
