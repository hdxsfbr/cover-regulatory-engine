"""Follow County tract identity through the public form; never execute returned scripts."""

import hashlib
import re
import time
import httpx
from bs4 import BeautifulSoup
from backend import evidence
from backend.gis import now

URL = "https://pw.lacounty.gov/smpm/landrecords/TractMaps.aspx"


def bounded(client, method, url, limit, deadline, cancelled, **kwargs):
    with client.stream(method, url, **kwargs) as response:
        response.raise_for_status()
        body = bytearray()
        for chunk in response.iter_bytes():
            if cancelled() or time.monotonic() > deadline:
                raise ValueError("Tract retrieval cancelled or exceeded 20 seconds")
            body.extend(chunk)
            if len(body) > limit:
                raise ValueError("County document exceeds retrieval limit")
        return bytes(body)


def retrieve(parcel, cancelled=lambda: False):
    deadline = time.monotonic() + 20
    legal = parcel.get("LegalDescription", "").upper()
    match = re.search(r"\bTR(?:ACT)?(?:\s+NO\.?)?[\s=#]*(\d+(?:-\d+)?)\b", legal)
    if not match:
        return {"status": "unreferenced", "kind": "tract-map"}
    result = {
        "kind": "tract-map",
        "tract": match[1],
        "status": "unavailable",
        "retrieved_at": now(),
        "discovery_url": URL,
        "origin": "live",
    }
    try:
        with httpx.Client(timeout=6, follow_redirects=False) as client:
            form = BeautifulSoup(
                bounded(client, "GET", URL, 1_000_000, deadline, cancelled),
                "html.parser",
            ).select_one("#aspnetForm")
            if form is None:
                raise ValueError("County tract search form unavailable")
            fields = {i["name"]: i.get("value", "") for i in form.select("input[name]")}
            fields["ctl00$main$bookTextBox"] = match[1]
            fields["ctl00$main$tractMapSearchButton"] = "Search"
            page = bounded(
                client, "POST", URL, 1_000_000, deadline, cancelled, data=fields
            ).decode("utf-8", errors="replace")
            found = re.search(
                r"window\.open\(['\"]((?:https:)?//pw\.lacounty\.gov/sur/nas/landrecords/tract/[A-Za-z0-9_./-]+\.pdf)['\"]\)",
                page,
            )
            if not found:
                raise ValueError("No public tract PDF returned for this tract identity")
            url = found[1] if found[1].startswith("https:") else "https:" + found[1]
            if ".." in url:
                raise ValueError("Invalid County document path")
            data = bounded(client, "GET", url, 30_000_000, deadline, cancelled)
            if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-1024:]:
                raise ValueError("County tract response is not a complete PDF")
            content_hash = hashlib.sha256(data).hexdigest()
            evidence.STORE.mkdir(exist_ok=True)
            (evidence.STORE / (content_hash + ".pdf")).write_bytes(data)
            result.update(status="available", source_url=url, content_hash=content_hash)
    except (httpx.HTTPError, ValueError, OSError) as error:
        result["error"] = str(error)
    return result
