import asyncio
import copy
import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from backend import research, store, questions
from backend import app as module

DATA = Path("data/sources/research-recorded")


def context():
    return json.loads(Path("data/fixtures/2202010006.json").read_text())


def test_permit_history_preserves_unknown_status_and_document():
    async def run():
        def handler(request):
            assert dict(request.url.params)["book"] == "2202"
            return httpx.Response(
                200, json=json.loads((DATA / "stagg-permits.json").read_text())
            )

        c = context()
        c["parcel"]["AIN"] = "2202004010"
        result = research.envelope("permits", c)
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            await research.permits(client, c, result)
        assert len(result["items"]) == 5
        assert result["items"][0]["document_available"]
        assert result["items"][1]["status"] == "Not supplied"
        assert "final approval" in result["warnings"][0]

    asyncio.run(run())


def test_planning_association_and_embedded_document_discovery():
    async def run():
        c = context()
        c["parcel"]["AIN"] = "2202004010"

        def handler(request):
            if "landbase" in request.url.path:
                data = json.loads((DATA / "stagg-landbase.json").read_text())
            elif "GetProjectData" in request.url.path:
                data = json.loads((DATA / "stagg-profile.json").read_text())
            else:
                return httpx.Response(200, text=(DATA / "ordinance.html").read_text())
            return httpx.Response(200, json=data)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = research.envelope("planning", c)
            await research.planning(client, c, result)
        cases = [i for i in result["items"] if i["group"] == "Case Numbers"]
        assert any(i.get("documents") for i in cases)
        assert all(
            "insidela" not in d["url"] for i in cases for d in i.get("documents", [])
        )
        assert any(i["value"] == "CPC-2019-1741-CPU" for i in cases)
        c["parcel"]["AIN"] = "9999999999"
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(ValueError, match="does not match"):
                await research.planning(client, c, research.envelope("planning", c))

    asyncio.run(run())


def test_partial_engineering_does_not_erase_working_layers():
    async def run():
        def handler(request):
            if "Master_street" in request.url.path:
                return httpx.Response(503)
            return httpx.Response(200, json={"features": []})

        c = context()
        result = research.envelope("engineering", c)
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            await research.engineering(client, c, result)
        assert result["status"] == "partial"
        assert [x["status"] for x in result["layers"]].count("no-match") == 4
        assert "title search" in result["warnings"][0]

    asyncio.run(run())


def test_transit_is_pedestrian_estimate_not_eligibility(monkeypatch):
    async def run():
        monkeypatch.setattr(research, "STOPS", None)
        c = context()
        point = research.parcel_shape(c).representative_point()
        lon, lat = research.TO_MAP(point.x, point.y)

        def handler(request):
            if request.url.host == "api.metro.net":
                return httpx.Response(
                    200,
                    json=[
                        {
                            "properties": {"stop_id": "1", "stop_name": "Test stop"},
                            "geometry": {"coordinates": [lon + 0.001, lat]},
                        }
                    ],
                )
            params = json.loads(request.url.params["json"])
            assert params["costing"] == "pedestrian"
            assert params["units"] == "miles"
            assert " " not in request.url.params["json"]
            return httpx.Response(
                200,
                json={
                    "trip": {
                        "status": 0,
                        "units": "miles",
                        "summary": {"length": 0.17, "time": 180},
                        "legs": [{"maneuvers": [{"instruction": "Walk east"}]}],
                    }
                },
            )

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = research.envelope("transit", c)
            await research.transit(client, c, result)
        assert result["items"][0]["walking_miles"] == 0.17
        assert result["items"][0]["route_status"] == "estimated"
        assert "eligibility not determined" in result["summary"].lower()
        assert "eligibility" not in result
        assert research.distance_miles((0, 0), (0, 1)) == pytest.approx(69.09, abs=0.1)

    asyncio.run(run())


def test_redirect_validation_and_bad_json_are_failures():
    async def run():
        seen = []

        def handler(request):
            seen.append(request.url.host)
            return httpx.Response(302, headers={"location": "http://127.0.0.1/private"})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(ValueError, match="approved"):
                await research.read(client, research.PRISM)
        assert seen == ["prism.dbs.lacity.gov"]

    asyncio.run(run())
    assert research.safe_url(None, "https://navigatela.lacity.org/") is None
    assert (
        research.safe_url(
            "navigatela/reports/centerline.cfm?PK=1", "https://navigatela.lacity.org/"
        )
        == "https://navigatela.lacity.org/navigatela/reports/centerline.cfm?PK=1"
    )
    assert research.safe_url("javascript:alert(1)") is None
    assert research.safe_url("https://evil.example/document.pdf") is None


def test_cached_refresh_and_capture_immutable_identity(monkeypatch):
    c = context()

    async def acquire(source, ctx, recorded):
        return {
            **research.envelope(source, ctx),
            "summary": "test record",
            "items": [
                {"title": "permit", "value": "ISSUED", "source_url": research.PRISM}
            ],
        }

    monkeypatch.setattr(research, "acquire", acquire)

    async def run():
        first = await research.fetch("permits", c)
        same = await research.fetch(
            "permits", {**c, "automatic_evidence": {"observations": [1]}}
        )
        assert same["id"] == first["id"]
        second = await research.fetch("permits", c, fresh=True)
        assert second["id"] != first["id"]
        captured = research.capture(c, {"permits": first["id"]})
        assert captured["permits"]["id"] == first["id"]
        legacy = {**first, "context_key": research.key(c, 2)}
        old_id = store.put("research", legacy)
        assert research.capture(c, {"permits": old_id})["permits"]["id"] == old_id
        altered = copy.deepcopy(c)
        altered["parcel"]["AIN"] = "9999999999"
        with pytest.raises(ValueError, match="different parcel"):
            research.capture(altered, {"permits": first["id"]})
        altered = copy.deepcopy(c)
        altered["records"]["Parcels"]["features"][0]["geometry"]["coordinates"][0][0][
            0
        ] += 1
        with pytest.raises(ValueError, match="different parcel"):
            research.capture(altered, {"permits": first["id"]})
        ev = questions.evidence_for(
            {
                "assessment": {"constraints": []},
                "request": {},
                "context": {"research": captured},
            }
        )
        assert "ISSUED" in ev["research-permits-0"]["text"]
        assert ev["research-permits-0"]["url"] == research.PRISM

    asyncio.run(run())


def test_scenario_saves_only_selected_server_research(monkeypatch):
    monkeypatch.setattr(module, "FIXTURE_MODE", True)
    client = TestClient(module.app)
    c = client.get("/api/parcels/2202010006/context").json()
    ctx = module.snapshot_context(c["snapshot_id"])
    r = research.envelope("permits", ctx)
    rid = store.put("research", r)
    project = client.post(
        "/api/projects", json={"name": "research test", "snapshot_id": c["snapshot_id"]}
    ).json()
    body = {
        "name": "saved",
        "snapshot_id": c["snapshot_id"],
        "research_ids": {"permits": rid},
    }
    saved = client.post(f"/api/projects/{project['id']}/scenarios", json=body)
    assert saved.status_code == 200, saved.text
    assert saved.json()["data"]["context"]["research"]["permits"]["id"] == rid
    assert "research" not in module.snapshot_context(c["snapshot_id"])
    body["research_ids"] = {"permits": "invalid"}
    assert (
        client.post(f"/api/projects/{project['id']}/scenarios", json=body).status_code
        == 409
    )
    body["research_ids"] = {}
    assert (
        client.post(f"/api/projects/{project['id']}/scenarios", json=body).status_code
        == 200
    )
    result = client.post(
        "/api/research/permits", json={"snapshot_id": c["snapshot_id"]}
    ).json()
    assert result["origin"] == "fixture" and result["status"] == "not-checked"


def test_rail_failure_retains_bus_candidates_and_no_false_clearance(monkeypatch):
    async def run():
        monkeypatch.setattr(research, "STOPS", None)
        c = context()
        point = research.parcel_shape(c).representative_point()
        lon, lat = research.TO_MAP(point.x, point.y)

        def handler(request):
            if "LACMTA_Rail" in request.url.path:
                return httpx.Response(503)
            if request.url.host == "api.metro.net":
                return httpx.Response(
                    200,
                    json=[
                        {
                            "properties": {"stop_id": "1", "stop_name": "Bus stop"},
                            "geometry": {"coordinates": [lon, lat]},
                        }
                    ],
                )
            return httpx.Response(503)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = research.envelope("transit", c)
            await research.transit(client, c, result)
        assert result["status"] == "partial"
        assert result["items"][0]["title"] == "Bus stop"
        assert result["items"][0]["route_status"] == "unavailable"
        assert result["layers"][1]["status"] == "unavailable"

    asyncio.run(run())


def test_engineering_polygon_hole_is_not_a_parcel_intersection(monkeypatch):
    from shapely.geometry import box

    monkeypatch.setattr(research, "parcel_shape", lambda _: box(4, 4, 6, 6))
    monkeypatch.setattr(
        research, "ENGINEERING", [("Easement", "Core/Master_landbase/MapServer/0", 0)]
    )

    async def run():
        def handler(request):
            return httpx.Response(
                200,
                json={
                    "features": [
                        {
                            "attributes": {"OBJECTID": 1},
                            "geometry": {
                                "rings": [
                                    list(box(0, 0, 10, 10).exterior.coords),
                                    list(box(3, 3, 7, 7).exterior.coords),
                                ]
                            },
                        }
                    ]
                },
            )

        c = context()
        result = research.envelope("engineering", c)
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            await research.engineering(client, c, result)
        assert result["status"] == "no-match"
        assert result["items"] == []

    asyncio.run(run())
