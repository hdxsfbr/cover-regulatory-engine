"""Public parcel research, kept separate from regulatory predicates and map extraction."""

import asyncio
import hashlib
import json
import math
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit, urlencode

import httpx
from bs4 import BeautifulSoup
from shapely.geometry import shape
from shapely.ops import unary_union
from backend import store
from backend.gis import now, TO_MAP

ZIMAS = "https://zimas.lacity.org"
PRISM = "https://prism.dbs.lacity.gov"
NAV = "https://maps.lacity.org/arcgis/rest/services"
METRO = "https://api.metro.net/LACMTA/stops/all"
ROUTER = "https://valhalla1.openstreetmap.de/route"
HOSTS = {
    "zimas.lacity.org",
    "planning.lacity.gov",
    "planning.lacity.org",
    "prism.dbs.lacity.gov",
    "maps.lacity.org",
    "navigatela.lacity.org",
    "api.metro.net",
    "valhalla1.openstreetmap.de",
    "clkrep.lacity.org",
    "cityclerk.lacity.org",
}
SOURCES = {
    "planning": ("Planning profile & cases", ZIMAS),
    "permits": ("Permit history", PRISM),
    "engineering": (
        "Engineering & easements",
        "https://navigatela.lacity.org/navigatela/",
    ),
    "transit": ("Transit & walking access", "https://api.metro.net/"),
}
INFLIGHT = {}
STOPS = None
STOP_LOCK = asyncio.Lock()
ROUTE_LOCK = asyncio.Lock()


def safe_url(value, base=""):
    if not value:
        return None
    url = urljoin(base, str(value).strip())
    parts = urlsplit(url)
    if (
        parts.scheme in ("http", "https")
        and parts.hostname in HOSTS
        and not parts.username
        and parts.port in (None, 443, 80)
    ):
        return (
            "https://"
            + parts.netloc
            + parts.path
            + ("?" + parts.query if parts.query else "")
            + ("#" + parts.fragment if parts.fragment else "")
        )
    return None


async def read(client, url, params=None):
    """Check each redirect before following; cap decompressed response size."""
    for _ in range(6):
        if not safe_url(url):
            raise ValueError("Source redirected outside approved public services")
        async with client.stream("GET", url, params=params) as response:
            if response.is_redirect:
                url = urljoin(str(response.url), response.headers["location"])
                params = None
                continue
            response.raise_for_status()
            chunks, size = [], 0
            async for chunk in response.aiter_bytes():
                size += len(chunk)
                if size > 8_000_000:
                    raise ValueError("Source response exceeds 8 MB limit")
                chunks.append(chunk)
            return b"".join(chunks), str(response.url)
    raise ValueError("Too many source redirects")


async def get_json(client, url, params=None):
    body, _ = await read(client, url, params)
    value = json.loads(body)
    if isinstance(value, dict) and value.get("error"):
        raise ValueError(str(value["error"])[:300])
    return value


def parcel_shape(context):
    features = context.get("records", {}).get("Parcels", {}).get("features", [])
    polygons = [shape(f["geometry"]) for f in features if f.get("geometry")]
    if not polygons:
        raise ValueError("Parcel geometry unavailable")
    geom = unary_union(polygons)
    if geom.is_empty or not geom.is_valid:
        raise ValueError("Parcel geometry invalid")
    return geom


def key(context, identity_version=1):
    return hashlib.sha256(
        json.dumps(
            {
                "parcel": context.get("parcel"),
                "geometry": [
                    f.get("geometry")
                    for f in context.get("records", {})
                    .get("Parcels", {})
                    .get("features", [])
                ],
                "version": identity_version,
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()


def envelope(source, context):
    title, url = SOURCES[source]
    return dict(
        source=source,
        title=title,
        source_url=url,
        ain=context["parcel"]["AIN"],
        context_key=key(context),
        retrieved_at=now(),
        origin="live",
        vintage="Not supplied by service",
        status="matched",
        items=[],
        warnings=[],
    )


async def arcgis(client, url, params):
    data = await get_json(
        client,
        url + "/query",
        {
            "f": "json",
            "outFields": "*",
            "returnGeometry": "false",
            "resultRecordCount": 100,
            **params,
        },
    )
    if not isinstance(data, dict) or not isinstance(data.get("features"), list):
        raise ValueError("Malformed GIS response")
    if any(not isinstance(f.get("attributes"), dict) for f in data["features"]):
        raise ValueError("Malformed GIS attributes")
    return data


async def planning(client, context, result):
    ain = result["ain"]
    url = ZIMAS + "/arcgis/rest/services/zm4/landbase/MapServer/105"
    land = await arcgis(client, url, {"where": f"BPP='{ain}'"})
    matches = [f["attributes"] for f in land["features"]]
    if any(m.get("BPP") != ain or not m.get("PIN") for m in matches):
        raise ValueError("City landbase response does not match selected APN")
    result["association"] = (
        "Exact APN → City PIN; case references may cover an area or the whole city."
    )
    result["next_action"] = (
        "Read applicable case decisions and conditions before accepting ordinary zoning assumptions."
    )
    result["warnings"].append(
        "A listed case is a reference, not a finding that its approvals or conditions apply to this project."
    )
    if land.get("exceededTransferLimit") or len(matches) > 4:
        result["warnings"].append(
            "Only the first four City PINs were retrieved. Open ZIMAS for complete coverage."
        )
        result["status"] = "partial"
    for match in matches[:4]:
        pin = match["PIN"]
        profile_url = (
            ZIMAS
            + "/zm4WS/GetProjectData?"
            + urlencode({"PIN": pin, "APN": "", "project": ""})
        )
        try:
            tabs = await get_json(client, profile_url)
            if not isinstance(tabs, list) or not all(
                isinstance(t, dict) and isinstance(t.get("Value"), list) for t in tabs
            ):
                raise ValueError("Malformed ZIMAS profile")
            apns = [
                str(v.get("Value", ""))
                for t in tabs
                for v in t["Value"]
                if v.get("Description") == "Assessor Parcel No. (APN)"
            ]
            if not any(ain in a.replace("-", "") for a in apns):
                raise ValueError("ZIMAS profile APN association could not be confirmed")
            for tab in tabs:
                if tab["Key"] == "Assessor Information":
                    continue
                for field in tab["Value"]:
                    value = field.get("Value")
                    if value is None or value == "":
                        continue
                    result["items"].append(
                        {
                            "title": field.get("Description", tab["Key"]),
                            "value": str(value),
                            "group": tab["Key"],
                            "pin": pin,
                            "source_url": safe_url(field.get("Link"), ZIMAS)
                            if field.get("Link")
                            else profile_url,
                        }
                    )
        except (httpx.HTTPError, ValueError, KeyError) as e:
            result["status"] = "partial"
            result["warnings"].append(f"PIN {pin}: {str(e)[:250]}")
    cases = [
        i
        for i in result["items"]
        if i["group"] == "Case Numbers" and i["source_url"] and i["value"] != "None"
    ]
    if len(cases) > 6:
        result["status"] = "partial"
        result["warnings"].append(
            "Document discovery limited to the first six case references; remaining references can be opened directly."
        )
    for item in cases[:6]:
        try:
            body, final_url = await read(client, item["source_url"])
            soup = BeautifulSoup(body, "html.parser")
            documents = []
            for script in soup.find_all("script"):
                for match in re.finditer(r"window\.\w+\s*=\s*(\[)", script.get_text()):
                    try:
                        rows, _ = json.JSONDecoder().raw_decode(
                            script.get_text()[match.start(1) :]
                        )
                        documents.extend(
                            row
                            for row in rows
                            if isinstance(row, dict) and row.get("ExternalUrl")
                        )
                    except ValueError:
                        pass
            if "casePddDocsGrid" in body.decode(errors="replace"):
                rows = await get_json(
                    client,
                    "https://planning.lacity.gov/pdiscaseinfo/api/Service/GetPddData",
                    {"caseNumbers": item["value"]},
                )
                if not isinstance(rows, list):
                    raise ValueError("Malformed Planning document list")
                documents.extend(rows)
            item["case_details"] = {
                row.select_one(".title").get_text(" ", strip=True): row.select_one(
                    ".data"
                ).get_text(" ", strip=True)
                for row in soup.select(".rowData")
                if row.select_one(".title") and row.select_one(".data")
            }
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            item["case_url"] = final_url
            item["documents"] = [
                {
                    "title": doc.get("DocType")
                    or doc.get("DocumentIdentifier")
                    or doc.get("CaseNumber")
                    or "Planning document",
                    "url": safe_url(doc["ExternalUrl"]),
                    "date": doc.get("DateModified"),
                    "approval_status": doc.get("ApprovalStatus"),
                }
                for doc in documents[:50]
                if isinstance(doc, dict) and safe_url(doc.get("ExternalUrl"))
            ]
            if len(documents) > 50:
                result["status"] = "partial"
                result["warnings"].append(
                    f"{item['value']}: document list limited to 50; open the case for the remainder."
                )
            for a in soup.find_all("a", href=True):
                link = safe_url(a["href"], final_url)
                if link and (
                    ".pdf" in link.lower()
                    or "/document" in link.lower()
                    or "/odocument/" in link.lower()
                ):
                    item["documents"].append(
                        {
                            "title": a.get_text(" ", strip=True) or "Source document",
                            "url": link,
                        }
                    )
            item["case_excerpt"] = soup.get_text(" ", strip=True)[:5000]
            item["document_status"] = (
                "linked"
                if item["documents"]
                else "No document links returned in case page; open case for its document tabs."
            )
        except (httpx.HTTPError, ValueError) as e:
            item["document_status"] = "unavailable"
            item["error"] = str(e)[:200] or type(e).__name__
            result["status"] = "partial"
    if not matches:
        result["status"] = "no-match"
    result["summary"] = (
        f"{len(matches)} City parcel match(es), {len(cases)} case/ordinance references."
    )


async def permits(client, context, result):
    ain = result["ain"]
    result["association"] = f"PRISM assessor search: {ain[:4]}-{ain[4:7]}-{ain[7:]}."
    result["next_action"] = (
        "Check permit scope and final inspection records for the existing buildings and proposed alterations."
    )
    result["warnings"] = [
        "A permit being issued does not establish final approval. No returned records does not establish an absence of permits or violations."
    ]
    seen = set()
    for offset in range(0, 200, 50):
        page = await get_json(
            client,
            PRISM + "/api/search/assessor",
            {
                "book": ain[:4],
                "page": ain[4:7],
                "parcel": ain[7:],
                "offset": offset,
                "limit": 50,
            },
        )
        if (
            not isinstance(page, dict)
            or not isinstance(page.get("hits"), list)
            or not isinstance(page.get("has_more"), bool)
        ):
            raise ValueError("Malformed PRISM results")
        for hit in page["hits"]:
            if not isinstance(hit, dict) or not hit.get("record_id"):
                raise ValueError("Malformed permit record")
            if hit["record_id"] in seen:
                continue
            seen.add(hit["record_id"])
            result["items"].append(
                {
                    "title": hit.get("usr_doc_nbr")
                    or hit.get("doc_nbrs")
                    or str(hit["record_id"]),
                    "value": " · ".join(
                        str(hit[k])
                        for k in ("doc_type", "sub_type", "status")
                        if hit.get(k)
                    ),
                    "date": hit.get("doc_date"),
                    "address": hit.get("address"),
                    "status": hit.get("status") or "Not supplied",
                    "record_id": hit["record_id"],
                    "source_url": safe_url(hit.get("pdf_url")) or PRISM,
                    "document_available": bool(safe_url(hit.get("pdf_url"))),
                }
            )
        if not page["has_more"]:
            break
    else:
        result["status"] = "partial"
        result["warnings"].append(
            "History exceeds the 200-record retrieval limit. Open PRISM for remaining records."
        )
    if not result["items"]:
        result["status"] = "no-match"
    result["summary"] = (
        f"{len(result['items'])} permit/building records; {sum(i['document_available'] for i in result['items'])} downloadable documents."
    )


ENGINEERING = [
    ("Mapped easement lines", "Core/Master_landbase/MapServer/0", 0),
    ("Sewer easements", "Core/Master_sewer_external/MapServer/9", 0),
    ("Nearby sewer pipes", "Core/Master_sewer_external/MapServer/7", 100),
    ("Adjacent streets", "Core/Master_street/MapServer/4", 100),
    ("Cadastral parcels", "Core/Master_landbase/MapServer/2", 0),
]


async def engineering(client, context, result):
    geom = parcel_shape(context)
    result["association"] = (
        "EPSG:2229 parcel intersection; street and sewer context within 100 feet. Nearby features are not parcel restrictions."
    )
    result["next_action"] = (
        "Review mapped easements and plan references; confirm dedication and service requirements with the applicable engineering office."
    )
    result["warnings"] = [
        "These selected layers are not a title search or a utility capacity/connection determination. GIS alignment and unmapped rights remain unresolved."
    ]
    result["layers"] = []

    async def layer(title, path, buffer):
        url = NAV + "/" + path
        bounds = geom.buffer(buffer).bounds
        params = {
            "geometry": ",".join(map(str, bounds)),
            "geometryType": "esriGeometryEnvelope",
            "inSR": 2229,
            "spatialRel": "esriSpatialRelIntersects",
            "returnGeometry": "true",
            "outSR": 2229,
        }
        try:
            data = await arcgis(client, url, params)
            items = []
            for f in data["features"]:
                g = f.get("geometry", {})
                from shapely.geometry import Polygon, MultiLineString

                feature = (
                    Polygon() if "rings" in g else MultiLineString(g.get("paths", []))
                )
                for ring in g.get("rings", []):
                    feature = feature.symmetric_difference(Polygon(ring))
                if feature.is_empty:
                    raise ValueError("Engineering feature has no usable geometry")
                distance = geom.distance(feature)
                if distance > buffer + 0.01:
                    continue
                attrs = {
                    k: v
                    for k, v in f["attributes"].items()
                    if v is not None
                    and str(v).strip()
                    and k not in ("SHAPE", "USER_ID", "TOOLTIP")
                }
                items.append(
                    {
                        "title": title,
                        "value": "Intersects mapped parcel"
                        if distance < 0.01
                        else f"{distance:.1f} ft from mapped parcel",
                        "source_url": safe_url(
                            attrs.get("NLA_URL"), "https://navigatela.lacity.org/"
                        )
                        or url,
                        "fields": attrs,
                        "distance_ft": round(distance, 1),
                    }
                )
            return {
                "title": title,
                "source_url": url,
                "status": "partial"
                if data.get("exceededTransferLimit")
                else ("matched" if items else "no-match"),
                "items": items,
            }
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return {
                "title": title,
                "source_url": url,
                "status": "unavailable",
                "items": [],
                "error": str(e)[:200] or type(e).__name__,
            }

    result["layers"] = await asyncio.gather(*(layer(*entry) for entry in ENGINEERING))
    result["items"] = [i for entry in result["layers"] for i in entry["items"]]
    if any(entry["status"] in ("partial", "unavailable") for entry in result["layers"]):
        result["status"] = (
            "partial"
            if any(entry["status"] != "unavailable" for entry in result["layers"])
            else "unavailable"
        )
    elif not result["items"]:
        result["status"] = "no-match"
    result["summary"] = (
        f"{sum(i['title'] in ('Mapped easement lines', 'Sewer easements') for i in result['items'])} mapped easement features; {sum(i['title'] == 'Nearby sewer pipes' for i in result['items'])} nearby sewer pipes. {len(ENGINEERING)} layers checked."
    )


def distance_miles(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, (*a, *b))
    h = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    return 3958.7613 * 2 * math.asin(min(1, math.sqrt(h)))


async def transit(client, context, result):
    global STOPS
    center = parcel_shape(context).representative_point()
    origin = TO_MAP(center.x, center.y)
    stops = []
    result["layers"] = []
    async with STOP_LOCK:
        if STOPS is None:
            STOPS = {}
        for agency in ("LACMTA", "LACMTA_Rail"):
            feed_url = f"https://api.metro.net/{agency}/stops/all"
            try:
                cached = STOPS.get(agency)
                if cached is None or time.monotonic() - cached[0] > 86400:
                    rows = await get_json(client, feed_url)
                    if (
                        not isinstance(rows, list)
                        or not rows
                        or not all(
                            isinstance(row.get("properties"), dict)
                            and len(row.get("geometry", {}).get("coordinates", [])) == 2
                            for row in rows
                        )
                    ):
                        raise ValueError("Malformed Metro stop response")
                    cached = (time.monotonic(), now(), rows)
                    STOPS[agency] = cached
                stops.extend({**row, "agency": agency} for row in cached[2])
                result["layers"].append(
                    {
                        "title": "Metro rail"
                        if agency.endswith("Rail")
                        else "Metro bus",
                        "source_url": feed_url,
                        "status": "matched",
                        "retrieved_at": cached[1],
                    }
                )
            except (httpx.HTTPError, ValueError) as e:
                result["status"] = "partial"
                result["layers"].append(
                    {
                        "title": agency,
                        "source_url": feed_url,
                        "status": "unavailable",
                        "error": str(e)[:200] or type(e).__name__,
                    }
                )
    if not stops:
        raise ValueError("Both Metro stop feeds are unavailable")
    result["association"] = (
        "Metro stop candidates within one mile of a representative point inside the mapped parcel."
    )
    result["next_action"] = (
        "Check the actual property entrance, walkable access, service and the applicable transit definition before claiming an ADU exception."
    )
    result["warnings"] = [
        "Metro coverage only; other transit operators are not checked.",
        "Walking routes are Valhalla estimates using © OpenStreetMap contributors, not surveyed access or statutory eligibility. The origin is not a verified entrance.",
        "Stop presence does not verify current service frequency, major-transit-stop status or parking/height eligibility.",
    ]
    result["origin_point"] = {
        "longitude": origin[0],
        "latitude": origin[1],
        "method": "GIS parcel representative point",
    }
    candidates = sorted(
        ((distance_miles(origin, s["geometry"]["coordinates"]), s) for s in stops),
        key=lambda pair: pair[0],
    )
    seen = set()
    for distance, stop in candidates:
        if distance > 1 or len(result["items"]) >= 3:
            break
        props = stop["properties"]
        identity = str(props.get("stop_id"))
        unique = (stop["agency"], identity)
        if unique in seen:
            continue
        seen.add(unique)
        dest = stop["geometry"]["coordinates"]
        item = {
            "title": props.get("stop_name") or identity,
            "value": f"{distance:.2f} mi straight-line",
            "stop_id": identity,
            "straight_line_miles": round(distance, 3),
            "source_url": f"https://api.metro.net/{stop['agency']}/stops/{identity}",
            "agency": stop["agency"],
            "coordinates": dest,
            "route_status": "unavailable",
        }
        try:
            params = {
                "locations": [
                    {"lat": origin[1], "lon": origin[0]},
                    {"lat": dest[1], "lon": dest[0]},
                ],
                "costing": "pedestrian",
                "units": "miles",
            }
            # Public demo fair-use: serialize requests and reuse each parcel result for 24h.
            async with ROUTE_LOCK:
                route = await get_json(
                    client, ROUTER, {"json": json.dumps(params, separators=(",", ":"))}
                )
                await asyncio.sleep(1)
            trip = route["trip"]
            if trip.get("status") != 0 or trip.get("units") != "miles":
                raise ValueError("No usable pedestrian route")
            miles = float(trip["summary"]["length"])
            if not math.isfinite(miles) or miles < 0:
                raise ValueError("Invalid walking distance")
            item.update(
                route_status="estimated",
                walking_miles=miles,
                walking_minutes=round(trip["summary"]["time"] / 60, 1),
                route_source=ROUTER
                + "?"
                + urlencode({"json": json.dumps(params, separators=(",", ":"))}),
                directions=[
                    m["instruction"]
                    for leg in trip.get("legs", [])
                    for m in leg.get("maneuvers", [])
                ][:30],
            )
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as e:
            item["route_error"] = str(e)[:200] or type(e).__name__
            result["status"] = "partial"
        result["items"].append(item)
    if not result["items"] and result["status"] != "partial":
        result["status"] = "no-match"
    result["summary"] = (
        f"{len(result['items'])} nearest Metro candidates; {sum(i['route_status'] == 'estimated' for i in result['items'])} estimated walking routes. Eligibility not determined."
    )

    estimates = [i["walking_miles"] for i in result["items"] if "walking_miles" in i]
    if estimates:
        result["summary"] = (
            f"Shortest of {len(estimates)} estimated walks: {min(estimates):.2f} mi. Metro candidates only; eligibility not determined."
        )


async def acquire(source, context, recorded=False):
    result = envelope(source, context)
    if recorded:
        result.update(
            status="not-checked",
            origin="fixture",
            summary="Live supplemental research is disabled in recorded mode.",
        )
        return result
    try:
        async with asyncio.timeout(100):
            async with httpx.AsyncClient(
                timeout=18,
                headers={
                    "User-Agent": "CoverRegulatoryPOC/1.0 (public parcel research)"
                },
            ) as client:
                await {
                    "planning": planning,
                    "permits": permits,
                    "engineering": engineering,
                    "transit": transit,
                }[source](client, context, result)
    except (httpx.HTTPError, ValueError, KeyError, TypeError, TimeoutError) as e:
        result.update(
            status="partial" if result["items"] else "unavailable",
            error=str(e)[:300] or type(e).__name__,
        )
        result["summary"] = (
            f"{len(result['items'])} records retained; source lookup incomplete."
            if result["items"]
            else "Source lookup unavailable. Retry or open the original source."
        )
    return result


async def fetch(source, context, fresh=False, recorded=False):
    parent = (
        key(context) + ":adapter3:" + source + (":fixture" if recorded else ":live")
    )

    async def run():
        prior = store.listing("research", parent)
        if prior and not fresh:
            record = prior[0]
            age = (
                datetime.now(timezone.utc)
                - datetime.fromisoformat(record["created_at"])
            ).total_seconds()
            if age < (
                60 if record["data"]["status"] in ("unavailable", "partial") else 86400
            ):
                return {**record["data"], "id": record["id"], "cached": True}
        value = await acquire(source, context, recorded)
        identity = store.put("research", value, parent)
        return {**value, "id": identity, "cached": False}

    if parent not in INFLIGHT:
        task = asyncio.create_task(run())
        INFLIGHT[parent] = task
        task.add_done_callback(lambda _: INFLIGHT.pop(parent, None))
    return await asyncio.shield(INFLIGHT[parent])


def capture(context, identities):
    results = {}
    # Early saved research used adapter versions 2/3 in the identity hash; keep those revisions readable.
    for source, identity in identities.items():
        if source not in SOURCES:
            raise ValueError("Unknown research source")
        record = store.get(identity, "research")["data"]
        if record["source"] != source or record["context_key"] not in {
            key(context, version) for version in (1, 2, 3)
        }:
            raise ValueError("Research belongs to a different parcel context")
        results[source] = {**record, "id": identity}
    return results
