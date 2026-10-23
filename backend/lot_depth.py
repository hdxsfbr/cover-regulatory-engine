"""Recorded-boundary midpoint depth; automation limits are not legal definitions."""

import hashlib
import json
import math
import re
from pathlib import Path
from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[1]
VERSION = "recorded-midpoint-v1"


def bearing(text):
    """Parse a printed quadrant bearing, without asking the model to do arithmetic."""
    cardinal = {
        "NORTH": (0.0, 1.0),
        "SOUTH": (0.0, -1.0),
        "EAST": (1.0, 0.0),
        "WEST": (-1.0, 0.0),
    }
    if str(text).strip().upper() in cardinal:
        return cardinal[str(text).strip().upper()]
    match = re.fullmatch(
        r"([NS])\s*(\d{1,2})[°º]\s*(\d{1,2})['′’]\s*(\d{1,2}(?:\.\d+)?)[\"″”]\s*([EW])",
        str(text).upper(),
    )
    if not match:
        raise ValueError("A printed quadrant bearing is required for each boundary")
    ns, degrees, minutes, seconds, ew = match.groups()
    d, m, s = float(degrees), float(minutes), float(seconds)
    if d > 90 or m >= 60 or s >= 60 or (d == 90 and (m or s)):
        raise ValueError("Invalid boundary bearing")
    theta = math.radians(d + m / 60 + s / 3600)
    return (
        math.sin(theta) * (1 if ew == "E" else -1),
        math.cos(theta) * (1 if ns == "N" else -1),
    )


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def unit(v):
    length = math.hypot(*v)
    if length < 0.001:
        raise ValueError("Degenerate boundary")
    return tuple(x / length for x in v)


def oriented(v, towards):
    return v if dot(v, towards) >= 0 else tuple(-x for x in v)


def derive(boundary, output, context, documents, geometry):
    if (
        context.get("jurisdiction") != "Los Angeles"
        or context.get("regime") != "Chapter 1"
    ):
        raise ValueError("Recorded midpoint depth is limited to LA Chapter 1")
    frontage = output.get("frontage", {})
    compass = [
        "north",
        "northeast",
        "east",
        "southeast",
        "south",
        "southwest",
        "west",
        "northwest",
    ]
    if frontage.get("confirmed") is not True or frontage.get("compass") not in compass:
        raise ValueError("Recorded depth requires confirmed street frontage")
    if (
        boundary.get("lot_type") != "interior"
        or boundary.get("rear_kind") != "opposite-boundary"
        or not boundary.get("rear_reason")
    ):
        raise ValueError(
            "Corner, through, gore or ambiguous rear-line cases require review"
        )
    if boundary.get("tract") != output["identity"].get("tract") or boundary.get(
        "lot"
    ) != output["identity"].get("lot"):
        raise ValueError("Recorded boundary tract/lot identity does not match")
    if (
        geometry is None
        or not geometry.is_valid
        or geometry.geom_type != "Polygon"
        or geometry.interiors
    ):
        raise ValueError("Depth requires a valid single parcel without holes")
    if context.get("records", {}).get("Parcels", {}).get("crs") != "EPSG:2229":
        raise ValueError("GIS depth corroboration requires feet in EPSG:2229")
    polygon = geometry.simplify(0.1, preserve_topology=True)
    if (
        len(polygon.exterior.coords) != 5
        or abs(polygon.area - polygon.convex_hull.area) > 0.1
    ):
        raise ValueError("Depth support requires a straight convex quadrilateral")
    edges = boundary.get("edges", [])
    if len(edges) != 4 or {e.get("role") for e in edges} != {
        "front",
        "rear",
        "side_a",
        "side_b",
    }:
        raise ValueError("Four distinct recorded boundary roles are required")
    parsed, sources = {}, []
    for edge in edges:
        length = edge.get("length_ft")
        if (
            type(length) not in (int, float)
            or not math.isfinite(length)
            or not 1 <= length <= 10000
        ):
            raise ValueError("Boundary length outside bounds")
        index = edge.get("document_index")
        if type(index) is not int or not 0 <= index < len(documents):
            raise ValueError("Unknown boundary source document")
        doc = documents[index]
        region = edge.get("region")
        if (
            doc.get("kind") != "tract-map"
            or type(edge.get("page")) is not int
            or edge["page"] not in doc["pages"]
            or not isinstance(region, list)
            or len(region) != 4
            or any(
                type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1
                for v in region
            )
            or not region[0] < region[2]
            or not region[1] < region[3]
            or not edge.get("printed_mark")
            or not edge.get("reason")
        ):
            raise ValueError(
                "Each boundary needs a recorded-map page, crop and printed marking"
            )
        numbers = re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", edge["printed_mark"])
        if not any(abs(float(n) - length) < 0.0001 for n in numbers):
            raise ValueError("Boundary length is not in its printed marking")
        parsed[edge["role"]] = (length, bearing(edge.get("bearing")))
        sources.append(
            {
                **edge,
                "document_hash": doc["content_hash"],
                "source_url": doc["source_url"],
            }
        )
    theta = math.radians(compass.index(frontage["compass"]) * 45)
    outward = (math.sin(theta), math.cos(theta))
    inward = tuple(-x for x in outward)
    a, b = [oriented(parsed[k][1], inward) for k in ("side_a", "side_b")]
    axis = unit(tuple(x + y for x, y in zip(a, b)))
    # shortcut: nearly parallel sides only; expand with separately reviewed irregular-axis rules.
    if dot(a, b) < math.cos(math.radians(0.05)) or dot(axis, inward) < math.cos(
        math.radians(25)
    ):
        raise ValueError(
            "Side bearings do not establish the supported mean-depth direction"
        )
    front = oriented(parsed["front"][1], (-axis[1], axis[0]))
    rear = oriented(parsed["rear"][1], front)
    if abs(dot(front, axis)) > math.sin(math.radians(1)) or dot(front, rear) < math.cos(
        math.radians(20)
    ):
        raise ValueError(
            "Front/rear direction falls outside supported opposite-boundary geometry"
        )
    left, right = parsed["side_a"][0], parsed["side_b"][0]
    width, rear_length = parsed["front"][0], parsed["rear"][0]
    # Try both side assignments; accept only a recorded boundary that closes within 0.25 ft.
    closure = []
    for (la, va), (lb, vb) in [((left, a), (right, b)), ((right, b), (left, a))]:
        back_a = tuple(la * x for x in va)
        back_b = tuple(width * x + lb * y for x, y in zip(front, vb))
        residual = math.dist(
            tuple(y - x for x, y in zip(back_a, back_b)),
            tuple(rear_length * x for x in rear),
        )
        if residual <= 0.25:
            closure.append(
                Polygon([(0, 0), tuple(width * x for x in front), back_b, back_a])
            )
    if not closure or not all(p.is_valid and p.area > 0 for p in closure):
        raise ValueError("Recorded boundary dimensions and bearings do not close")
    depth = (left * dot(a, axis) + right * dot(b, axis)) / 2
    coords = list(polygon.exterior.coords)
    gis_edges = [
        (
            math.dist(coords[i], coords[i + 1]),
            unit(tuple(y - x for x, y in zip(coords[i], coords[i + 1]))),
        )
        for i in range(4)
    ]
    sides = sorted(
        length
        for length, direction in gis_edges
        if abs(dot(direction, axis)) >= math.cos(math.radians(3))
    )
    if len(sides) != 2 or any(
        abs(x - y) / y > 0.04 for x, y in zip(sorted([left, right]), sides)
    ):
        raise ValueError("Recorded side lengths or directions conflict with GIS")
    if (
        abs(depth - sum(sides) / 2) / (sum(sides) / 2) > 0.04
        or abs(closure[0].area - geometry.area) / geometry.area > 0.08
    ):
        raise ValueError("Recorded depth or boundary area conflicts with GIS")
    assumptions = [
        "Uses the identified street frontage and opposite mapped rear boundary; current legal lot-line applicability still requires review.",
        "Straight interior quadrilateral with effectively parallel sides; no 10-foot gore-lot chord, corner/through-lot or curved-boundary interpretation.",
        "Recorded dimensions are approximate source readings, not a current survey or confirmation that no later lot-line changes occurred.",
    ]
    transverse = [
        length
        for length, direction in gis_edges
        if abs(dot(direction, axis)) < math.cos(math.radians(3))
    ]
    if any(
        abs(x - y) / y > 0.04
        for x, y in zip(sorted([width, rear_length]), sorted(transverse))
    ):
        assumptions.append(
            "Recorded front/rear boundary lengths differ from GIS by more than 4%; depth is corroborated by the side lengths, but boundary width/current legal configuration needs review."
        )
    citations = json.loads(
        (ROOT / "data/sources/measurement-guidance/pins.json").read_text()
    )
    for citation in citations:
        if (
            hashlib.sha256((ROOT / citation["path"]).read_bytes()).hexdigest()
            != citation["source_hash"]
        ):
            raise ValueError("Lot-depth definition/guidance changed; review derivation")
    value = round(depth, 2)
    primary = next(s for s in sources if s["role"] == "side_a")
    reason = f"Approximate midpoint depth: ({left:g} ft + {right:g} ft) / 2 = {value:g} ft (mean side-bearing projection). Uses the opposite recorded rear boundary. {boundary['rear_reason']}"
    return {
        "key": "lot_depth_ft",
        "value": value,
        "units": "ft",
        "method": "derived-midpoint-depth",
        "derivation_version": VERSION,
        "page": primary["page"],
        "region": primary["region"],
        "printed_mark": primary["printed_mark"],
        "document_hash": primary["document_hash"],
        "source_url": primary["source_url"],
        "reason": reason,
        "operands": sources,
        "citations": citations,
        "assumptions": assumptions,
        "confidence_reason": "Deterministic derivation from machine-read recorded boundaries, corroborated against GIS side lengths; not surveyed or legally verified.",
    }
