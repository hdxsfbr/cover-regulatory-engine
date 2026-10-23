"""Per-edge setback clipping in State Plane US survey feet."""

import math
from shapely.geometry import Polygon, shape, mapping
from shapely.geometry.polygon import orient
from shapely.ops import transform
from backend.gis import TO_MAP

DIRECTIONS = {
    "north": (0, 1),
    "northeast": (1, 1),
    "east": (1, 0),
    "southeast": (1, -1),
    "south": (0, -1),
    "southwest": (-1, -1),
    "west": (-1, 0),
    "northwest": (-1, 1),
}


def envelope(geometry, frontage, setbacks):
    polygon = shape(geometry)
    if not polygon.is_valid or polygon.is_empty or polygon.geom_type != "Polygon":
        raise ValueError("A single valid parcel polygon is required")
    exterior = Polygon(polygon.exterior).simplify(0.1, preserve_topology=True)
    if (
        len(exterior.exterior.coords) != 5
        or exterior.area / exterior.minimum_rotated_rectangle.area < 0.97
    ):
        raise ValueError("Edge roles need review for this irregular or multipart lot")
    direction = DIRECTIONS.get(frontage.get("compass"))
    if not direction or not frontage.get("street") or not frontage.get("reason"):
        raise ValueError("Document-backed frontage orientation is missing")
    coords = list(orient(exterior, sign=1).exterior.coords)
    edges = []
    for a, b in zip(coords, coords[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        nx, ny = -dy / length, dx / length
        score = (-nx * direction[0] - ny * direction[1]) / math.hypot(*direction)
        edges.append({"a": a, "b": b, "normal": (nx, ny), "score": score})
    scores = sorted(range(4), key=lambda i: edges[i]["score"], reverse=True)
    front = scores[0]
    if edges[front]["score"] - edges[scores[1]]["score"] < 0.15:
        raise ValueError("Frontage compass cannot distinguish adjoining edges")
    result = polygon
    reach = (
        max(
            polygon.bounds[2] - polygon.bounds[0], polygon.bounds[3] - polygon.bounds[1]
        )
        * 10
        + 1000
    )
    annotations = []
    for i, e in enumerate(edges):
        role = (
            "front-yard"
            if i == front
            else "rear-yard"
            if i == (front + 2) % 4
            else "side-yard"
        )
        distance = setbacks[role]
        if (
            type(distance) not in (int, float)
            or not math.isfinite(distance)
            or distance < 0
        ):
            raise ValueError("Invalid setback")
        a, b = e["a"], e["b"]
        nx, ny = e["normal"]
        tx, ty = ny, -nx
        left = (a[0] + nx * distance - tx * reach, a[1] + ny * distance - ty * reach)
        right = (b[0] + nx * distance + tx * reach, b[1] + ny * distance + ty * reach)
        clip = Polygon(
            [
                left,
                right,
                (right[0] + nx * reach, right[1] + ny * reach),
                (left[0] + nx * reach, left[1] + ny * reach),
            ]
        )
        result = result.intersection(clip)
        annotations.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [TO_MAP(*a), TO_MAP(*b)],
                },
                "properties": {
                    "kind": "setback-edge",
                    "category": role,
                    "setback_ft": distance,
                },
            }
        )
    return {
        "type": "FeatureCollection",
        "features": annotations
        + [
            {
                "type": "Feature",
                "geometry": mapping(transform(TO_MAP, result)),
                "properties": {"kind": "setback-envelope", "area_sqft": result.area},
            }
        ],
    }


def for_assessment(context, assessment):
    try:
        geometry = context["records"]["Parcels"]["features"][0]["geometry"]
        extraction = context.get("automatic_evidence", {})
        if extraction.get("shape") != "rectangle":
            raise ValueError(
                "A corroborated rectangular map interpretation is required"
            )
        if extraction.get("frontage", {}).get("confirmed") is not True:
            raise ValueError(
                "Frontage orientation has not been explicitly established by the document reading"
            )
        selected = {
            r["category"]: r
            for r in assessment["constraints"]
            if r["category"] in ("front-yard", "side-yard", "rear-yard")
        }
        if len(selected) != 3:
            raise ValueError("This package does not establish all three edge setbacks")
        setbacks = {}
        conditional = False
        for category, r in selected.items():
            if r["value"] is not None:
                setbacks[category] = r["value"]
            elif r.get("conditional"):
                setbacks[category] = r["conditional"]["value"]
                conditional = True
            else:
                raise ValueError("A required setback is unresolved")
        output = envelope(geometry, extraction.get("frontage") or {}, setbacks)
        output["metadata"] = {
            "status": "conditional" if conditional else "evaluated",
            "scope": "Setback envelope only; excludes easements, passageways, fire separation and other unmodeled constraints",
            "calculation_crs": "EPSG:2229",
            "linear_units": "US survey foot",
            "output_crs": "OGC:CRS84",
            "rule_set_version": assessment["rule_set_version"],
            "document_hash": context["document"]["content_hash"],
            "frontage": extraction["frontage"],
            "assumptions": list(
                dict.fromkeys(
                    a
                    for r in selected.values()
                    for a in (r.get("conditional") or {}).get("assumptions", [])
                )
            ),
            "citations": [c for r in selected.values() for c in r["citations"]],
        }
        return output
    except (ValueError, KeyError, TypeError, IndexError) as e:
        return {"status": "withheld", "reason": str(e)}
