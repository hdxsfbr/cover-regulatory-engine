import asyncio
import copy
import hashlib
import json
import httpx
import pytest
from backend import evidence, gis

PARCEL = {
    "AIN": "2202010006",
    "Assr_Map": "2202-010",
    "LegalDescription": "TRACT # 16180 LOT  108",
}
PDF = b"%PDF-1.4\nexample\n%%EOF"


def fetch(handler):
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await evidence.retrieve(PARCEL, client)

    return asyncio.run(run())


def test_document_trust_boundaries(tmp_path, monkeypatch):
    monkeypatch.setattr(evidence, "STORE", tmp_path)
    ok = fetch(
        lambda r: httpx.Response(
            200, content=PDF, headers={"content-type": "application/pdf"}
        )
    )
    assert (
        ok["status"] == "available"
        and (tmp_path / (ok["content_hash"] + ".pdf")).read_bytes() == PDF
    )
    assert evidence.reference({})["status"] == "unreferenced"
    assert evidence.reference({"Assr_Map": "../../private"})["status"] == "unreferenced"
    for response in [
        httpx.Response(503),
        httpx.Response(200, content=b"<html/>"),
        httpx.Response(
            200, content=b"%PDF-broken", headers={"content-type": "application/pdf"}
        ),
        httpx.Response(302, headers={"location": "https://example.com/private"}),
    ]:
        assert fetch(lambda r: response)["status"] == "unavailable"
    monkeypatch.setattr(evidence, "LIMIT", 5)
    assert (
        fetch(
            lambda r: httpx.Response(
                200, content=PDF, headers={"content-type": "application/pdf"}
            )
        )["status"]
        == "unavailable"
    )


def candidate(tmp_path):
    h = hashlib.sha256(PDF).hexdigest()
    (tmp_path / (h + ".pdf")).write_bytes(PDF)
    return {
        "ain": PARCEL["AIN"],
        "map_id": "2202-010",
        "legal_description": PARCEL["LegalDescription"],
        "tract": "16180",
        "lot": "108",
        "page": 1,
        "location": "Louise row, lot 108",
        "method": "visual-transcription",
        "document_hash": h,
        "key": "lot_depth_ft",
        "value": 120,
        "units": "ft",
    }


def test_review_and_identity(tmp_path, monkeypatch):
    monkeypatch.setattr(evidence, "STORE", tmp_path)
    c = candidate(tmp_path)
    for key, value in [
        ("page", 0),
        ("units", "m"),
        ("value", True),
        ("value", float("nan")),
        ("ain", "other"),
        ("lot", ""),
    ]:
        with pytest.raises(ValueError):
            evidence.review({**c, key: value}, "reviewer")
    o = evidence.review(c, "Codex transcription review")
    (tmp_path / "observations.json").write_text(json.dumps([c, o]))
    ctx = {
        "parcel": PARCEL,
        "records": {
            n: {"status": "no-match", "features": []} for n in evidence.SCREENING
        },
        "applicability_fingerprint": "base",
    }
    d = {
        "status": "available",
        "content_hash": c["document_hash"],
        "source_url": "https://example.test",
    }
    attached = evidence.attach(copy.deepcopy(ctx), d)
    assert len(attached["observations"]) == 1
    assert attached["observations"][0]["status"] == "reviewed"
    assert evidence.select(attached, [o["id"]], {})["lot_depth_ft"]["value"] == 120
    with pytest.raises(ValueError):
        evidence.select(attached, [o["id"]], {"lot_depth_ft": 99})
    with pytest.raises(ValueError):
        evidence.select(attached, ["forged"], {})
    newer = evidence.attach(copy.deepcopy(ctx), {**d, "content_hash": "0" * 64})
    assert (
        newer["observations"][0]["status"] == "stale"
        and newer["applicability_fingerprint"] is None
    )
    different = copy.deepcopy(ctx)
    different["parcel"] = {**PARCEL, "AIN": "2202010005"}
    assert not evidence.attach(different, d)["observations"]


def test_registered_maps_and_acceptance():
    from backend.rules import assess, CHECKS

    for ain in ("2202010006", "2202010009"):
        path = (
            gis.ROOT / "data/fixtures" / f"{ain}.json"
            if ain.endswith("009")
            else evidence.STORE / "recorded-contexts" / f"{ain}.json"
        )
        raw = json.loads(path.read_text())
        # Separate successful live recording preserves the original timeout fixture.
        ctx = gis.summarize(raw["records"])
        assert ctx["zone"] == "R1-1" and ctx["zoning_status"] == "resolved"
        ctx = evidence.attach(ctx, recorded=True)
        assert {o["value"] for o in ctx["observations"]} == {50, 120, 6000}
        ids = [o["id"] for o in ctx["observations"]]
        result = assess(
            ctx,
            "single-family",
            {"building_height_ft": 18, "roof_slope_percent": 20},
            {k: True for k in CHECKS},
            "Hypothetical ordinary project; map measurements accepted, legal conditions assumed.",
            observation_ids=ids,
        )
        assert [r["value"] for r in result["constraints"]] == [20, 5, 15, 28, 2700]
        assert all(r["confidence"] == "medium" for r in result["constraints"])
        assert (
            result["constraints"][0]["inputs"]["lot_depth_ft"]["origin"]
            == "document-accepted"
        )
        missing = assess(ctx, "single-family", {}, {})
        assert all(r["blockers"] for r in missing["constraints"])
        assert missing["constraints"][0]["blockers"][0]["target"] == "parcel-evidence"
        for project in ("adu", "guest-house"):
            assert all(
                r["value"] is None and r["blockers"]
                for r in assess(ctx, project, {}, {})["constraints"]
            )
    raw = json.loads((gis.ROOT / "data/fixtures/2202010005.json").read_text())
    assert not evidence.attach(gis.summarize(raw["records"]), recorded=True)[
        "observations"
    ]


def test_screening_and_lifecycle():
    from backend.tests.test_core import context_records
    from backend.rules import assess, CHECKS

    records = context_records()
    records[evidence.SCREENING[0]].update(
        status="matched", features=copy.deepcopy(records["Parcels"]["features"])
    )
    ctx = gis.summarize(records)
    assert ctx["records"][evidence.SCREENING[0]]["intersections"][0]["area_sqft"] == 100
    r = assess(ctx, "single-family", {}, {k: True for k in CHECKS}, "test")
    assert all(x["value"] is None for x in r["constraints"])
    records[evidence.SCREENING[0]]["features"][0]["geometry"] = None
    assert (
        gis.summarize(records)["records"][evidence.SCREENING[0]]["status"]
        == "unavailable"
    )
    records = context_records()
    ctx = gis.summarize(records)
    first = evidence.attach(copy.deepcopy(ctx))["applicability_fingerprint"]
    assert first
    assert assess(ctx, "single-family", {}, {})["applicability_assertions"] == {
        "outside_hillside_coastal": True
    }
    records[evidence.SCREENING[0]]["status"] = "unavailable"
    assert evidence.attach(gis.summarize(records))["applicability_fingerprint"] is None


def test_conflicts_and_revision(tmp_path, monkeypatch):
    monkeypatch.setattr(evidence, "STORE", tmp_path)
    c = candidate(tmp_path)
    a = evidence.review(c, "one")
    b = evidence.review({**c, "value": 125}, "two")
    (tmp_path / "observations.json").write_text(json.dumps([a, b]))
    ctx = {"parcel": PARCEL, "records": {}, "applicability_fingerprint": "base"}
    ctx = evidence.attach(
        ctx, {"status": "available", "content_hash": c["document_hash"]}
    )
    assert all(o["status"] == "conflict" for o in ctx["observations"])
    with pytest.raises(ValueError):
        evidence.select(ctx, [b["id"]], {})


def test_document_within_context_deadline(monkeypatch):
    from backend.tests.test_core import context_records

    records = context_records()
    records["Parcels"]["features"][0]["properties"].update(PARCEL)

    async def query(client, name, params):
        return copy.deepcopy(records[name])

    async def stalled(*args):
        await asyncio.sleep(10)

    original = asyncio.wait_for

    async def short(awaitable, timeout):
        return await original(awaitable, 0.02)

    monkeypatch.setattr(gis, "query", query)
    monkeypatch.setattr(evidence, "retrieve", stalled)
    monkeypatch.setattr(gis.asyncio, "wait_for", short)

    async def run():
        async with httpx.AsyncClient() as c:
            return await gis.context_for(PARCEL["AIN"], c, False)

    ctx = asyncio.run(run())
    assert ctx["document"]["status"] == "unavailable"
    assert ctx["zone"] == "R1-1"
    assert ctx["applicability_fingerprint"] is None


def test_screening_query_rejects_partial_and_failures():
    async def run(payload, status=200):
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(status, json=payload)
            )
        ) as c:
            return await gis.query(c, evidence.SCREENING[0], {})

    for payload, status in [
        ({"features": [], "exceededTransferLimit": True}, 200),
        ({"error": {"message": "bad"}}, 200),
        ({}, 503),
    ]:
        assert asyncio.run(run(payload, status))["status"] == "unavailable"


def test_api_selection_and_invalidated_snapshot(monkeypatch):
    import backend.app as api
    from fastapi.testclient import TestClient

    monkeypatch.setattr(api, "FIXTURE_MODE", True)
    client = TestClient(api.app)
    ctx = client.get("/api/parcels/2202010009/context?compact=true").json()
    ids = [o["id"] for o in ctx["observations"]]
    body = {"snapshot_id": ctx["snapshot_id"], "observation_ids": ids}
    assert client.post("/api/assessments", json=body).status_code == 200
    assert (
        client.post("/api/assessments", json={**body, "verified": True}).status_code
        == 422
    )
    assert (
        client.post(
            "/api/assessments", json={**body, "observation_ids": ["fake"]}
        ).status_code
        == 422
    )
    original = api.fixture

    def changed(ain):
        ctx = original(ain)
        ctx["applicability_fingerprint"] = None
        return ctx

    monkeypatch.setattr(api, "fixture", changed)
    client.get("/api/parcels/2202010009/context?fresh=true")
    # Unknown refreshed evidence cannot retain earlier document acceptance.
    assert client.post("/api/assessments", json=body).status_code == 410


def test_ambiguous_reading_and_derived_area(tmp_path, monkeypatch):
    monkeypatch.setattr(evidence, "STORE", tmp_path)
    c = candidate(tmp_path)
    with pytest.raises(ValueError):
        evidence.review({**c, "ambiguous": True}, "reviewer")
    with pytest.raises(ValueError):
        evidence.review({**c, "lot": "111"}, "reviewer")
    area = {
        **c,
        "key": "lot_area_sqft",
        "units": "sq ft",
        "method": "derived-rectangle",
        "derivation": "width times depth",
        "value": 6000,
        "dimensions_ft": {"lot_width_ft": 50, "lot_depth_ft": 120},
    }
    assert evidence.review(area, "reviewer")["value"] == 6000
    with pytest.raises(ValueError):
        evidence.review({**area, "value": 7500}, "reviewer")


@pytest.mark.parametrize(
    "ain",
    [
        "2202010005",
        "2126037055",
        "4328021043",
        "5138014112",
        "4103012026",
        "2202010006",
    ],
)
def test_recorded_exclusion_cohort(ain):
    from backend.app import fixture
    from backend.rules import assess

    ctx = fixture(ain)
    for project in ("single-family", "adu", "guest-house"):
        result = assess(ctx, project, {}, {})
        assert all(r["value"] is None and r["blockers"] for r in result["constraints"])
        if project != "single-family" or ain in ("4328021043", "5138014112"):
            assert all(
                r["value"] is None and r["blockers"] for r in result["constraints"]
            )
