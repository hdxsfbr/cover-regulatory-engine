"""Public map retrieval and locally reviewed transcriptions, never legal verification."""

import argparse
import asyncio
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "data/parcel-evidence"
LIMIT = 10_000_000
HOST = "maps.assessor.lacounty.gov"
SCREENING = ("Hillside Ordinance", "Coastal Commission Permit Area")
BOUNDS = {
    "lot_width_ft": (1, 10000),
    "lot_depth_ft": (1, 10000),
    "lot_area_sqft": (1, 10000000),
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def reference(parcel):
    ref = parcel.get("Assr_Map", "")
    result = {
        "map_id": ref,
        "ain": parcel.get("AIN"),
        "legal_description": parcel.get("LegalDescription"),
        "status": "unreferenced",
        "vintage": "unknown",
        "origin": "live",
    }
    if isinstance(ref, str) and re.fullmatch(r"\d{4}-\d{3}", ref):
        result.update(
            status="unavailable",
            source_url=f"https://{HOST}/GeoCortex/Essentials/PAIS/REST/sites/PAIS/Resources/ParcelMap?MapId={ref}-&f=file",
        )
    return result


async def retrieve(parcel, client):
    result = reference(parcel)
    if result["status"] == "unreferenced":
        return result
    result["retrieved_at"] = datetime.now(timezone.utc).isoformat()
    try:
        async with asyncio.timeout(12):
            url = result["source_url"]
            for _ in range(4):
                async with client.stream("GET", url, follow_redirects=False) as r:
                    if r.is_redirect:
                        target = r.url.join(r.headers["location"])
                        if (
                            target.scheme != "https"
                            or target.host != HOST
                            or target.port not in (None, 443)
                        ):
                            raise ValueError("Unapproved document redirect")
                        url = str(target)
                        continue
                    r.raise_for_status()
                    if (
                        "application/pdf"
                        not in r.headers.get("content-type", "").lower()
                    ):
                        raise ValueError("Document is not a PDF")
                    data = bytearray()
                    async for chunk in r.aiter_bytes():
                        data.extend(chunk)
                        if len(data) > LIMIT:
                            raise ValueError("Document exceeds 10 MB limit")
                    if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-1024:]:
                        raise ValueError("Invalid or truncated PDF")
                    content_hash = hashlib.sha256(data).hexdigest()
                    STORE.mkdir(parents=True, exist_ok=True)
                    (STORE / f"{content_hash}.pdf").write_bytes(data)
                    result.update(status="available", content_hash=content_hash)
                    return result
            raise ValueError("Too many document redirects")
    except (httpx.HTTPError, ValueError, TimeoutError, KeyError, OSError) as e:
        result["error"] = str(e) or type(e).__name__
    return result


def validate(observation):
    o = observation
    for key in (
        "ain",
        "map_id",
        "legal_description",
        "lot",
        "tract",
        "location",
        "method",
        "document_hash",
        "key",
        "units",
    ):
        if not isinstance(o.get(key), str) or not o[key].strip():
            raise ValueError(f"Missing observation {key}")
    if not re.fullmatch(r"\d{10}", o["ain"]) or not re.fullmatch(
        r"\d{4}-\d{3}", o["map_id"]
    ):
        raise ValueError("Invalid parcel/map identity")
    legal = o["legal_description"].upper()
    if not re.search(
        r"\bTR(?:ACT)?[\s=#]*" + re.escape(o["tract"]) + r"\b", legal
    ) or not re.search(r"\bLOT\s+" + re.escape(o["lot"]) + r"\b", legal):
        raise ValueError("Tract/lot does not match legal description")
    if not re.fullmatch(r"[a-f0-9]{64}", o["document_hash"]):
        raise ValueError("Invalid document hash")
    if type(o.get("page")) is not int or o["page"] < 1:
        raise ValueError("Invalid page")
    if o.get("ambiguous") or o["method"] not in (
        "visual-transcription",
        "derived-rectangle",
    ):
        raise ValueError("Ambiguous or unsupported extraction method")
    bounds = BOUNDS.get(o["key"])
    value = o.get("value")
    if (
        not bounds
        or type(value) not in (int, float)
        or not math.isfinite(value)
        or not bounds[0] <= value <= bounds[1]
    ):
        raise ValueError("Invalid observation value")
    if o["units"] != ("sq ft" if o["key"] == "lot_area_sqft" else "ft"):
        raise ValueError("Invalid units")
    data = (STORE / (o["document_hash"] + ".pdf")).read_bytes()
    if hashlib.sha256(data).hexdigest() != o["document_hash"]:
        raise ValueError("Document hash mismatch")
    if o["key"] == "lot_area_sqft" and (
        o.get("method") != "derived-rectangle" or not o.get("derivation")
    ):
        raise ValueError("Area needs an explicit rectangular derivation")
    if o["key"] == "lot_area_sqft":
        dims = o.get("dimensions_ft", {})
        if (
            set(dims) != {"lot_width_ft", "lot_depth_ft"}
            or any(
                type(v) not in (int, float)
                or not math.isfinite(v)
                or not 1 <= v <= 10000
                for v in dims.values()
            )
            or dims["lot_width_ft"] * dims["lot_depth_ft"] != value
        ):
            raise ValueError("Derived area must match its explicit width and depth")
    return o


def review(candidate, reviewer):
    if not reviewer.strip():
        raise ValueError("Reviewer required")
    o = validate({k: v for k, v in candidate.items() if k not in ("review", "id")})
    o["review"] = {
        "reviewer": reviewer,
        "at": datetime.now(timezone.utc).isoformat(),
        "scope": "transcription-only",
        "digest": digest(o),
    }
    o["id"] = digest(o)
    return o


def attach(context, document=None, recorded=False):
    parcel = context.get("parcel", {})
    doc = document if document is not None else reference(parcel)
    observations = []
    path = STORE / "observations.json"
    candidates = json.loads(path.read_text()) if path.exists() else []
    for o in candidates:
        if (
            o.get("ain") != parcel.get("AIN")
            or o.get("map_id") != parcel.get("Assr_Map")
            or o.get("legal_description") != parcel.get("LegalDescription")
        ):
            continue
        try:
            validate(o)
            base = {k: v for k, v in o.items() if k not in ("review", "id")}
            if (
                o.get("review", {}).get("digest") != digest(base)
                or not o["review"].get("reviewer")
                or not o["review"].get("at")
                or o["review"].get("scope") != "transcription-only"
            ):
                continue
            if o.get("id") != digest({k: v for k, v in o.items() if k != "id"}):
                continue
            if recorded and document is None:
                doc.update(status="available", content_hash=o["document_hash"])
            current = (
                doc.get("content_hash") == o["document_hash"]
                and doc["status"] == "available"
            )
            observations.append(
                {
                    **o,
                    "status": "reviewed" if current else "stale",
                    "source_url": doc.get("source_url"),
                }
            )
            if current:
                doc["vintage"] = o.get("document_vintage", "unknown")
        except (ValueError, KeyError, OSError, TypeError):
            continue
    for o in observations:
        if o["key"] == "lot_area_sqft" and any(
            not any(
                p["key"] == key
                and p["value"] == value
                and p["document_hash"] == o["document_hash"]
                and p["status"] == "reviewed"
                for p in observations
            )
            for key, value in o["dimensions_ft"].items()
        ):
            o["status"] = "stale"
    conflicts = {
        key
        for key in BOUNDS
        if len(
            {
                o["value"]
                for o in observations
                if o["key"] == key and o["status"] == "reviewed"
            }
        )
        > 1
    }
    for o in observations:
        if o["key"] in conflicts:
            o["status"] = "conflict"
    if recorded:
        doc["origin"] = "fixture"
    context["document"] = doc
    context["observations"] = observations
    fingerprint = context.get("applicability_fingerprint")
    screens = {
        n: context["records"].get(n, {"status": "not-checked"}) for n in SCREENING
    }
    uncertain = (
        doc["status"] == "unavailable"
        or any(r["status"] not in ("matched", "no-match") for r in screens.values())
        or any(o["status"] != "reviewed" for o in observations)
    )
    context["applicability_fingerprint"] = (
        None
        if not fingerprint or uncertain
        else digest(
            {
                "base": fingerprint,
                "document": doc.get("content_hash"),
                "observations": sorted(o["id"] for o in observations),
                "screening": {
                    n: {
                        "status": r["status"],
                        "features": sorted(
                            json.dumps(f, sort_keys=True) for f in r.get("features", [])
                        ),
                    }
                    for n, r in screens.items()
                },
            }
        )
    )
    return context


def select(context, ids, inputs):
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate observation selection")
    selected = {}
    for oid in ids:
        o = next((o for o in context.get("observations", []) if o["id"] == oid), None)
        if (
            not o
            or o["status"] != "reviewed"
            or o["document_hash"] != context.get("document", {}).get("content_hash")
            or context["document"]["status"] != "available"
        ):
            raise ValueError(
                "Observation is unavailable, changed or conflicting; refresh and review evidence"
            )
        if (
            o["ain"] != context.get("parcel", {}).get("AIN")
            or o["key"] in selected
            or o["key"] in inputs
        ):
            raise ValueError(
                "Choose either one document observation or a manual override for each dimension"
            )
        selected[o["key"]] = o
    return selected


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Review parcel map transcriptions (not legal applicability)"
    )
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--reviewer", required=True)
    args = parser.parse_args()
    candidate = json.loads(args.candidate.read_text())
    reviewed = review(candidate, args.reviewer)
    path = STORE / "observations.json"
    existing = json.loads(path.read_text()) if path.exists() else []
    existing = [
        o
        for o in existing
        if not (o["ain"] == reviewed["ain"] and o["key"] == reviewed["key"])
    ]
    path.write_text(json.dumps([*existing, reviewed], indent=2) + "\n")
    print(reviewed["id"])
