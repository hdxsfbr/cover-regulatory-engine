import asyncio
import copy
import json
import time
import httpx
from fastapi.testclient import TestClient
from backend import gis
import backend.app as api
from backend.tests.test_core import context_records


def codes(context):
    return {d["code"] for d in context["diagnostics"]}


def test_recorded_reasons_and_missing_sources():
    for ain, expected in [
        ("2202010006", "source_unavailable"),
        ("2126037055", "zoning_multiple_matches"),
        ("2202010005", "zoning_coverage_gap"),
    ]:
        raw = json.loads((gis.ROOT / "data/fixtures" / f"{ain}.json").read_text())
        ctx = gis.summarize(raw["records"])
        assert expected in codes(ctx)
        if ain == "2202010006":
            assert not {
                "zoning_multiple_matches",
                "zoning_coverage_gap",
                "zoning_no_match",
            } & codes(ctx)
            assert any(d["sources"] == ["Chapter 1 zoning"] for d in ctx["diagnostics"])
    records = context_records()
    records["Chapter 1 zoning"].update(status="no-match", features=[])
    assert "zoning_no_match" in codes(gis.summarize(records))
    records["Specific plans"]["status"] = "not-checked"
    assert "source_not_checked" in codes(gis.summarize(records))
    records["Parcels"]["features"][0]["geometry"] = None
    assert "invalid_geometry" in codes(gis.summarize(records))


def test_applicability_comparison():
    records = context_records()
    baseline = gis.summarize(records)["applicability_fingerprint"]
    assert baseline
    newer = copy.deepcopy(records)
    for r in newer.values():
        r.update(retrieved_at="later", origin="cached")
    assert gis.summarize(newer)["applicability_fingerprint"] == baseline
    newer["Buildings"]["status"] = "unavailable"
    assert gis.summarize(newer)["applicability_fingerprint"] == baseline
    newer["Specific plans"]["status"] = "unavailable"
    assert gis.summarize(newer)["applicability_fingerprint"] is None
    for field, value in [
        ("City boundary", "unavailable"),
        ("Chapter 1 zoning", "unavailable"),
    ]:
        changed = copy.deepcopy(records)
        changed[field]["status"] = value
        assert gis.summarize(changed)["applicability_fingerprint"] is None
    changed = copy.deepcopy(records)
    changed["Parcels"]["features"][0]["geometry"]["coordinates"] = [
        [[0, 0], [9, 0], [9, 10], [0, 10], [0, 0]]
    ]
    assert gis.summarize(changed)["applicability_fingerprint"] != baseline
    changed = copy.deepcopy(records)
    changed["Specific plans"].update(
        status="matched", features=copy.deepcopy(records["Parcels"]["features"])
    )
    changed["Specific plans"]["features"].append(
        copy.deepcopy(changed["Specific plans"]["features"][0])
    )
    changed["Specific plans"]["features"][1]["properties"]["plan"] = "second"
    first = gis.summarize(changed)["applicability_fingerprint"]
    changed["Specific plans"]["features"].reverse()
    assert (
        gis.summarize(changed)["applicability_fingerprint"] == first
        and first != baseline
    )
    changed["Specific plans"]["features"][0]["geometry"] = None
    assert gis.summarize(changed)["applicability_fingerprint"] is None


def test_fresh_cache_and_snapshot_recovery(monkeypatch):
    records = context_records()
    state = {"failed": False, "calls": 0}

    def transport(request):
        state["calls"] += 1
        name = next(
            n for n, s in gis.SOURCES.items() if str(request.url) == s["url"] + "/query"
        )
        if state["failed"] and name == "Chapter 1 zoning":
            raise httpx.ReadTimeout("Synthetic timeout")
        return httpx.Response(200, json={"features": records[name]["features"]})

    async def lookup(ain, **kwargs):
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(transport)
        ) as client:
            return await gis.context_for(ain, client, **kwargs)

    monkeypatch.setattr(api, "FIXTURE_MODE", False)
    monkeypatch.setattr(api, "context_for", lookup)
    gis.CACHE.clear()
    client = TestClient(api.app)
    old = client.get("/api/parcels/1234567890/context").json()
    assert old["zoning_status"] == "resolved"
    calls = state["calls"]
    cached = client.get("/api/parcels/1234567890/context").json()
    assert (
        state["calls"] == calls and cached["records"]["Parcels"]["origin"] == "cached"
    )
    state["failed"] = True
    fresh = client.get("/api/parcels/1234567890/context?fresh=true").json()
    assert (
        fresh["snapshot_id"] != old["snapshot_id"]
        and fresh["zoning_status"] == "needs-review"
    )
    assert fresh["records"]["Buildings"]["status"] == "no-match"
    assert (
        fresh["records"]["Parcels"]["retrieved_at"]
        != old["records"]["Parcels"]["retrieved_at"]
    )
    assert api.SNAPSHOTS[old["snapshot_id"]][1]["zoning_status"] == "resolved"
    assert "1234567890" not in gis.CACHE
    assert (
        client.get("/api/parcels/1234567890/context").json()["zoning_status"]
        == "needs-review"
    )
    state["failed"] = False
    recovered = client.get("/api/parcels/1234567890/context?fresh=true").json()
    assert recovered["zoning_status"] == "resolved" and "1234567890" in gis.CACHE
    assert api.SNAPSHOTS[fresh["snapshot_id"]][1]["zoning_status"] == "needs-review"
    gis.CACHE.clear()


def test_fixture_fresh_is_replay(monkeypatch):
    monkeypatch.setattr(api, "FIXTURE_MODE", True)

    async def forbidden(*args, **kwargs):
        raise AssertionError("Recorded mode must not query upstream")

    monkeypatch.setattr(api, "context_for", forbidden)
    response = (
        TestClient(api.app).get("/api/parcels/2202010006/context?fresh=true").json()
    )
    assert response["mode"] == "fixture" and "source_unavailable" in codes(response)
    assert all(r["origin"] == "fixture" for r in response["records"].values())


def test_overall_budget_retains_completed_sources():
    async def run():
        records = context_records()

        async def transport(request):
            name = next(
                n
                for n, s in gis.SOURCES.items()
                if str(request.url) == s["url"] + "/query"
            )
            if name == "Chapter 1 zoning":
                await asyncio.sleep(60)
            return httpx.Response(200, json={"features": records[name]["features"]})

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(transport)
        ) as client:
            started = time.monotonic()
            ctx = await gis.context_for("1234567890", client, False)
            elapsed = time.monotonic() - started
            assert 24 <= elapsed < 30
            assert ctx["records"]["Parcels"]["status"] == "matched"
            assert ctx["records"]["Chapter 1 zoning"]["status"] == "unavailable"
            assert ctx["records"]["Specific plans"]["status"] == "no-match"
            assert "zoning_multiple_matches" not in codes(ctx)

    asyncio.run(run())
    gis.CACHE.clear()


def test_older_success_cannot_repopulate_cache_after_new_failure():
    async def run():
        records = context_records()
        arrived = asyncio.Event()
        release = asyncio.Event()

        async def slow_success(request):
            name = next(
                n
                for n, s in gis.SOURCES.items()
                if str(request.url) == s["url"] + "/query"
            )
            if name == "Chapter 1 zoning":
                arrived.set()
                await release.wait()
            return httpx.Response(200, json={"features": records[name]["features"]})

        def failure(request):
            raise httpx.ReadTimeout("Newer attempt failed")

        gis.CACHE.clear()
        async with (
            httpx.AsyncClient(
                transport=httpx.MockTransport(slow_success)
            ) as old_client,
            httpx.AsyncClient(transport=httpx.MockTransport(failure)) as new_client,
        ):
            old = asyncio.create_task(gis.context_for("1234567890", old_client, False))
            await arrived.wait()
            newer = await gis.context_for("1234567890", new_client, False)
            assert newer["zoning_status"] == "needs-review"
            release.set()
            assert (await old)["zoning_status"] == "resolved"
            assert "1234567890" not in gis.CACHE and "1234567890" not in gis.INFLIGHT

    asyncio.run(run())


def test_compact_response_preserves_full_snapshot_and_assessment(monkeypatch):
    monkeypatch.setattr(api, "FIXTURE_MODE", True)
    client = TestClient(api.app)
    full = client.get("/api/parcels/2202010006/context").json()
    compact_response = client.get("/api/parcels/2202010006/context?compact=true")
    compact = compact_response.json()
    assert len(compact_response.content) < 30000
    assert len(compact_response.content) < len(json.dumps(full)) / 10
    assert (
        compact["map"] == full["map"] and compact["diagnostics"] == full["diagnostics"]
    )
    assert compact["applicability_fingerprint"] == full["applicability_fingerprint"]
    for name, record in compact["records"].items():
        assert "features" not in record and "query" not in record
        assert record["source_url"] == full["records"][name]["source_url"]
    snapshot = api.SNAPSHOTS[compact["snapshot_id"]][1]
    assert (
        snapshot["records"]["City boundary"]["features"]
        == full["records"]["City boundary"]["features"]
    )
    results = []
    for ctx in (full, compact):
        response = client.post(
            "/api/assessments", json={"snapshot_id": ctx["snapshot_id"]}
        ).json()
        response.pop("snapshot_id")
        results.append(response)
    assert results[0] == results[1]
