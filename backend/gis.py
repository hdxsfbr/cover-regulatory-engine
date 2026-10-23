"""Bounded public GIS reads and spatial evidence. No zoning adjudication."""

import asyncio
import copy
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from backend import evidence as parcel_evidence
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely import transform
from shapely.geometry.polygon import orient

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    s["name"]: s
    for s in json.loads((ROOT / "data/sources/gis-manifest.json").read_text())
}
OVERLAYS = ("Historic overlays", "Specific plans", "Design overlays")
TO_MAP = Transformer.from_crs(2229, 4326, always_xy=True).transform
CACHE = {}
INFLIGHT = {}


def now():
    return datetime.now(timezone.utc).isoformat()


def query_filter(value):
    value = value.strip()
    if not value or len(value) > 160 or any(ord(c) < 32 for c in value):
        raise ValueError("Enter an address or a ten-digit APN.")
    digits = re.sub(r"[-\s]", "", value)
    if digits.isdigit():
        if len(digits) != 10:
            raise ValueError("APN must contain ten digits.")
        return f"AIN='{digits}'"
    if any(c in value for c in "%_"):
        raise ValueError("Wildcards are not supported.")
    normalized = re.sub(r"[,.]", " ", value.upper())
    for long, short in {
        "AVENUE": "AVE",
        "STREET": "ST",
        "BOULEVARD": "BLVD",
        "DRIVE": "DR",
        "ROAD": "RD",
        "PLACE": "PL",
        "COURT": "CT",
        "LANE": "LN",
    }.items():
        normalized = re.sub(r"\b" + long + r"\b", short, normalized)
    normalized = re.sub(r"(\b\d{5})-\d{4}\s*$", r"\1", normalized)
    normalized = " ".join(normalized.split())
    escaped = normalized.replace("'", "''")
    house = re.match(r"^(\d+)\s", normalized)
    prefix = f"SitusHouseNo='{house[1]}' AND " if house else ""
    return prefix + f"UPPER(SitusFullAddress) LIKE '%{escaped}%'"


async def query(client, name, params):
    source = SOURCES[name]
    url = source["url"] + "/query"
    parameters = {
        "f": "geojson",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "2229",
        **params,
    }
    record = {
        "source_url": source["url"],
        "retrieved_at": now(),
        "vintage": source.get("vintage", "unknown"),
        "origin": "live",
        "crs": "EPSG:2229",
        "query": parameters,
    }
    try:
        # POST keeps detailed parcel polygons below proxy URL-length limits.
        async with client.stream("POST", url, data=parameters) as response:
            response.raise_for_status()
            chunks = []
            size = 0
            async for chunk in response.aiter_bytes():
                size += len(chunk)
                if size > 16_000_000:
                    raise ValueError("Source response exceeds size limit")
                chunks.append(chunk)
        data = json.loads(b"".join(chunks))
        if not isinstance(data, dict):
            raise ValueError("Malformed feature response")
        if data.get("error"):
            raise ValueError(str(data["error"].get("message", "ArcGIS error")))
        if data.get("exceededTransferLimit") or data.get("properties", {}).get(
            "exceededTransferLimit"
        ):
            raise ValueError("Source result is incomplete; refine query")
        if not isinstance(data.get("features"), list):
            raise ValueError("Malformed feature response")
        if any(
            not isinstance(f, dict) or not isinstance(f.get("properties"), dict)
            for f in data["features"]
        ):
            raise ValueError("Malformed feature record")
        record.update(
            status="matched" if data["features"] else "no-match",
            features=data["features"],
        )
    except (httpx.HTTPError, ValueError) as error:
        record.update(
            status="unavailable", features=[], error=str(error) or type(error).__name__
        )
    return record


def polygon(feature):
    if not isinstance(feature.get("geometry"), dict):
        raise ValueError("Invalid or missing polygon geometry")
    geometry = shape(feature["geometry"])
    if (
        geometry.geom_type not in ("Polygon", "MultiPolygon")
        or not geometry.is_valid
        or geometry.is_empty
        or geometry.area <= 0
    ):
        raise ValueError("Invalid or missing polygon geometry")
    return geometry


def map_feature(feature):
    return {
        **feature,
        "geometry": mapping(transform(polygon(feature), TO_MAP, interleaved=False)),
    }


def summarize(records):
    parcel_record = records["Parcels"]
    context = {
        "records": records,
        "jurisdiction": "needs-review",
        "zoning_status": "needs-review",
        "zone_matches": [],
        "zone": None,
        "regime": None,
        "map": {"type": "FeatureCollection", "features": []},
        "issues": [],
        "diagnostics": [],
        "applicability_fingerprint": None,
        "checked_overlays": list(OVERLAYS),
    }

    def diagnose(code, message, sources, retryable=False):
        context["diagnostics"].append(
            {
                "code": code,
                "message": message,
                "sources": sources,
                "retryable": retryable,
            }
        )
        context["issues"].append(message)

    for name, record in records.items():
        if record["status"] == "unavailable":
            diagnose(
                "source_unavailable",
                f"{name} source unavailable; its evidence is missing. Refresh parcel sources to try again.",
                [name],
                True,
            )
        elif record["status"] == "not-checked":
            diagnose(
                "source_not_checked",
                f"{name} was not checked because parcel evidence was unresolved.",
                [name],
                True,
            )
    if parcel_record["status"] != "matched" or len(parcel_record["features"]) != 1:
        diagnose(
            "parcel_unresolved",
            "Parcel was not resolved uniquely; retry the selected parcel or refine the search.",
            ["Parcels"],
            True,
        )
        return context
    feature = parcel_record["features"][0]
    context["parcel"] = feature["properties"]
    geometry_source = "Parcels"
    try:
        parcel = polygon(feature)
        context["estimated_area_sqft"] = parcel.area
        context["map"]["features"].append(
            {
                **map_feature(feature),
                "properties": {**feature["properties"], "kind": "parcel"},
            }
        )
        geometry_source = "City boundary"
        city = records["City boundary"]
        if city["status"] in ("matched", "no-match"):
            la = [
                polygon(f)
                for f in city["features"]
                if f["properties"].get("CITY_NAME") == "Los Angeles"
            ]
            if not la or parcel.intersection(unary_union(la)).area == 0:
                context["jurisdiction"] = "outside-city"
            elif unary_union(la).covers(parcel):
                context["jurisdiction"] = "Los Angeles"
            else:
                diagnose(
                    "jurisdiction_boundary_gap",
                    "Parcel crosses or does not align with the city boundary.",
                    ["Parcels", "City boundary"],
                )
        zones = []
        covered = []
        for name, regime in [
            ("Chapter 1 zoning", "Chapter 1"),
            ("Chapter 1A zoning", "Chapter 1A"),
        ]:
            geometry_source = name
            record = records[name]
            for f in record["features"]:
                z = polygon(f)
                area = parcel.intersection(z).area
                fraction = area / parcel.area
                match = {
                    "zone": f["properties"].get("ZONE_CMPLT"),
                    "regime": regime,
                    "area_sqft": area,
                    "fraction": fraction,
                    "possible_sliver": 0 < area < 1 and fraction < 0.0001,
                    "boundary_touch": area == 0,
                    "source_url": record["source_url"],
                }
                context["zone_matches"].append(match)
                if area > 0:
                    zones.append(match)
                    covered.append(z)
        complete = all(
            records[n]["status"] in ("matched", "no-match")
            for n in ("Chapter 1 zoning", "Chapter 1A zoning")
        )
        if complete and len(zones) == 1 and unary_union(covered).covers(parcel):
            context.update(
                zoning_status="resolved",
                zone=zones[0]["zone"],
                regime=zones[0]["regime"],
            )
        if len(zones) > 1:
            diagnose(
                "zoning_multiple_matches",
                "Multiple positive-area zoning matches require review; all matches are retained.",
                ["Chapter 1 zoning", "Chapter 1A zoning"],
            )
        if complete and not zones:
            diagnose(
                "zoning_no_match",
                "Completed zoning queries returned no positive-area match for this parcel.",
                ["Chapter 1 zoning", "Chapter 1A zoning"],
            )
        elif complete and not unary_union(covered).covers(parcel):
            diagnose(
                "zoning_coverage_gap",
                "Returned zoning geometry does not cover the entire parcel; the coverage gap requires review.",
                ["Parcels", "Chapter 1 zoning", "Chapter 1A zoning"],
            )
        for name in OVERLAYS:
            geometry_source = name
            for f in records[name]["features"]:
                polygon(f)
    except (ValueError, KeyError, TypeError) as error:
        diagnose(
            "invalid_geometry",
            f"{geometry_source}: invalid or missing geometry; review required ({error}).",
            [geometry_source],
        )
        context["jurisdiction"] = context["zoning_status"] = "needs-review"
    for f in records["Buildings"]["features"]:
        try:
            context["map"]["features"].append(
                {
                    **map_feature(f),
                    "properties": {**f["properties"], "kind": "building"},
                }
            )
        except (ValueError, KeyError, TypeError):
            diagnose(
                "invalid_geometry",
                "Invalid building footprint omitted from map.",
                ["Buildings"],
            )
    for name in parcel_evidence.SCREENING:
        record = records.get(name)
        if record and record["status"] == "matched":
            try:
                record["intersections"] = [
                    {
                        "feature_id": f.get("id", f["properties"].get("OBJECTID")),
                        "area_sqft": parcel.intersection(polygon(f)).area,
                        "boundary_touch": parcel.intersection(polygon(f)).area == 0,
                    }
                    for f in record["features"]
                ]
            except (ValueError, KeyError, TypeError, UnboundLocalError):
                record["status"] = "unavailable"
                record["error"] = "Invalid screening geometry"
    context["applicability_fingerprint"] = applicability_fingerprint(context)
    return context


def applicability_fingerprint(context):
    names = [
        "Parcels",
        "City boundary",
        "Chapter 1 zoning",
        "Chapter 1A zoning",
        *OVERLAYS,
    ]
    if (
        context["jurisdiction"] == "needs-review"
        or context["zoning_status"] != "resolved"
    ):
        return None
    evidence = {}
    for name in names:
        record = context["records"][name]
        if record["status"] not in ("matched", "no-match"):
            return None
        evidence[name] = {
            "status": record["status"],
            "crs": record.get("crs"),
            "features": sorted(
                json.dumps(f, sort_keys=True, separators=(",", ":"))
                for f in record["features"]
            ),
        }
    evidence["jurisdiction"] = context["jurisdiction"]
    evidence["zone_matches"] = sorted(
        json.dumps(z, sort_keys=True) for z in context["zone_matches"]
    )
    return hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()


async def search(value, client=None):
    where = query_filter(value)
    if client is None:
        async with httpx.AsyncClient(timeout=12) as owned:
            return await search(value, owned)
    return await query(
        client,
        "Parcels",
        {
            "where": where,
            "resultRecordCount": "21",
            "returnGeometry": "false",
            "outFields": "AIN,APN,SitusFullAddress",
        },
    )


async def context_for(ain, client=None, use_cache=True):
    where = query_filter(ain)
    if not re.fullmatch(r"\d{10}", ain):
        raise ValueError("Invalid parcel identifier")
    if not use_cache:
        CACHE.pop(ain, None)
    if use_cache and ain in CACHE and time.monotonic() - CACHE[ain][0] < 900:
        result = copy.deepcopy(CACHE[ain][1])
        for record in result["records"].values():
            record["origin"] = "cached"
        if result.get("document"):
            result["document"]["origin"] = "cached"
        return result
    if client is None:
        async with httpx.AsyncClient(timeout=22) as owned:
            return await context_for(ain, owned, use_cache)
    records = {}
    document = None
    request_token = object()
    INFLIGHT[ain] = request_token

    async def collect():
        nonlocal document
        records["Parcels"] = await query(
            client, "Parcels", {"where": where, "resultRecordCount": "2"}
        )
        parcel = records["Parcels"]
        if parcel["status"] != "matched" or len(parcel["features"]) != 1:
            return
        g = polygon(parcel["features"][0])
        polygons = [g] if g.geom_type == "Polygon" else list(g.geoms)
        rings = []
        for part in polygons:
            part = orient(part, sign=-1)
            rings.append(list(part.exterior.coords))
            rings.extend(list(r.coords) for r in part.interiors)
        params = {
            "geometry": json.dumps(
                {"rings": rings, "spatialReference": {"wkid": 2229}}
            ),
            "geometryType": "esriGeometryPolygon",
            "inSR": "2229",
            "spatialRel": "esriSpatialRelIntersects",
            "resultRecordCount": "1000",
        }

        async def one(name):
            records[name] = await query(
                client,
                name,
                {
                    **params,
                    **(
                        {"distance": "100", "units": "esriSRUnit_Foot"}
                        if name == "Coastal Zone (state boundary)"
                        else {}
                    ),
                },
            )

        async def document_query():
            nonlocal document
            document = await parcel_evidence.retrieve(
                parcel["features"][0]["properties"], client
            )

        await asyncio.gather(
            document_query(), *(one(name) for name in SOURCES if name != "Parcels")
        )

    try:
        await asyncio.wait_for(collect(), timeout=25)
    except (TimeoutError, ValueError, KeyError, TypeError):
        pass
    except asyncio.CancelledError:
        if INFLIGHT.get(ain) is request_token:
            INFLIGHT.pop(ain, None)
        raise
    parcel_unresolved = "Parcels" in records and (
        records["Parcels"]["status"] != "matched"
        or len(records["Parcels"]["features"]) != 1
    )
    for name, source in SOURCES.items():
        records.setdefault(
            name,
            {
                "status": "not-checked" if parcel_unresolved else "unavailable",
                "features": [],
                "source_url": source["url"],
                "origin": "live",
                "retrieved_at": now(),
                "vintage": source.get("vintage", "unknown"),
                "crs": "EPSG:2229",
                "error": "Parcel unresolved; layer not queried"
                if parcel_unresolved
                else "Lookup budget exhausted or invalid parcel geometry",
            },
        )
    result = parcel_evidence.attach(summarize(records), document)
    latest = INFLIGHT.get(ain) is request_token
    if latest:
        INFLIGHT.pop(ain, None)
    if (
        latest
        and result["document"]["status"] != "unavailable"
        and all(r["status"] in ("matched", "no-match") for r in records.values())
    ):
        if len(CACHE) >= 100:
            CACHE.pop(next(iter(CACHE)))
        CACHE[ain] = (time.monotonic(), copy.deepcopy(result))
    return result
