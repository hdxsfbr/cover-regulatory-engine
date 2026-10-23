"""Reassess retained public-source contexts; never claim replay is a live lookup."""

import copy
import json
import time
from collections import Counter
from pathlib import Path
from backend import rules, summary

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/delivery"
contexts = {}
for path in sorted(
    [*DATA.glob("*-context.json"), *DATA.glob("*-positive-candidate.json")]
):
    c = json.loads(path.read_text())
    if not c.get("parcel", {}).get("AIN"):
        continue
    ain = c["parcel"]["AIN"]
    extraction = path.with_name(
        path.name.replace("-context.json", "-extraction.json").replace(
            "-candidate.json", "-extraction.json"
        )
    )
    if extraction.exists():
        e = json.loads(extraction.read_text())
        c["automatic_evidence"] = e
        c["machine_observations"] = e.get("observations", [])
    contexts[ain] = c
stagg = json.loads((DATA / "stagg-depth/live-browser-proof.json").read_text())[
    "context"
]
contexts[stagg["parcel"]["AIN"]] = stagg
rows = []
for ain, context in sorted(contexts.items()):
    for project in ("single-family", "adu", "guest-house"):
        design = {
            "building_height_ft": 16,
            "roof_slope_percent": 20,
            "proposed_area_sqft": 600,
            "existing_floor_area_sqft": 0,
        }
        choices = (
            {}
            if project == "single-family"
            else {
                "new_detached": True,
                "has_kitchen": project == "adu",
                "rented": False,
                "temporary_guests": True,
            }
        )
        for mode in ("source-facts-and-design-only", "hypothetical-applicability"):
            checks = (
                choices
                if mode == "source-facts-and-design-only"
                else {**{k: True for k in rules.CHECKS}, **choices}
            )
            start = time.perf_counter()
            result = rules.assess(
                copy.deepcopy(context),
                project,
                design,
                checks,
                "Hypothetical design; applicability assertions are not source verification"
                if mode == "hypothetical-applicability"
                else "Proposed design; no manual applicability assertions",
            )
            result["summary"] = summary.summarize(result, design)
            rows.append(
                {
                    "ain": ain,
                    "address": context["parcel"].get("SitusFullAddress"),
                    "project_type": project,
                    "mode": mode,
                    "elapsed_ms": (time.perf_counter() - start) * 1000,
                    "assessment": result,
                }
            )
counts = {
    mode: {
        project: dict(
            Counter(
                r["assessment"]["status"]
                for r in rows
                if r["mode"] == mode and r["project_type"] == project
            )
        )
        for project in ("single-family", "adu", "guest-house")
    }
    for mode in ("source-facts-and-design-only", "hypothetical-applicability")
}
references = json.loads((DATA / "reference-readings.json").read_text())["cases"]
comparisons = []
for ain, ref in references.items():
    observed = {
        o["key"]: o["value"]
        for o in contexts.get(ain, {}).get("machine_observations", [])
    }
    expected = ref["expected_scalar_dimensions"]
    errors = {
        k: v
        for k, v in observed.items()
        if k not in expected or abs(v - expected[k]) > 0.1
    }
    comparisons.append(
        {
            "ain": ain,
            "observed": observed,
            "expected": expected,
            "missing": sorted(set(expected) - set(observed)),
            "errors": errors,
        }
    )
    assert not errors, (ain, errors)
assert any(
    abs(o["value"] - 179.55) < 0.01
    for o in stagg["machine_observations"]
    if o["key"] == "lot_depth_ft"
)
report = {
    "kind": "current-code replay of retained public-source contexts; not newly fetched GIS",
    "parcels": len(contexts),
    "assessments": len(rows),
    "counts": counts,
    "map_reference_checks": comparisons,
    "results": rows,
}
(DATA / "poc-polish/cohort.json").write_text(json.dumps(report, indent=2))
print(
    json.dumps(
        {
            k: report[k]
            for k in (
                "kind",
                "parcels",
                "assessments",
                "counts",
                "map_reference_checks",
            )
        },
        indent=2,
    )
)
