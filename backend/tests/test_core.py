import asyncio
import copy
import json
import time
import httpx
import pytest
from shapely.geometry import Polygon, mapping
from fastapi.testclient import TestClient
from backend import gis, rules
from backend.app import app, SNAPSHOTS


def feature(coords, properties=None):
    return {
        "type": "Feature",
        "geometry": mapping(Polygon(coords)),
        "properties": properties or {},
    }


def context_records():
    f = feature([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)], {"AIN": "1234567890"})
    records = {
        name: {
            "status": "no-match",
            "features": [],
            "source_url": s["url"],
            "origin": "fixture",
            "retrieved_at": "2026-10-22",
            "crs": "EPSG:2229",
        }
        for name, s in gis.SOURCES.items()
    }
    records["Parcels"].update(status="matched", features=[f])
    city = copy.deepcopy(f)
    city["properties"] = {"CITY_NAME": "Los Angeles"}
    zone = copy.deepcopy(f)
    zone["properties"] = {"ZONE_CMPLT": "R1-1"}
    records["City boundary"].update(status="matched", features=[city])
    records["Chapter 1 zoning"].update(status="matched", features=[zone])
    return records


def test_spatial_ambiguity_and_holes():
    records = context_records()
    assert gis.summarize(records)["zone"] == "R1-1"
    records["Chapter 1 zoning"]["features"].append(
        feature(
            [(9.9999, 0), (11, 0), (11, 10), (9.9999, 10), (9.9999, 0)],
            {"ZONE_CMPLT": "RD5-1"},
        )
    )
    result = gis.summarize(records)
    assert result["zoning_status"] == "needs-review"
    assert result["zone_matches"][1]["possible_sliver"]
    records = context_records()
    records["Parcels"]["features"][0]["geometry"]["coordinates"] += (
        ((2, 2), (2, 3), (3, 3), (3, 2), (2, 2)),
    )
    assert gis.summarize(records)["estimated_area_sqft"] == 99


def test_invalid_geometry_and_jurisdiction():
    records = context_records()
    records["City boundary"]["features"] = []
    assert gis.summarize(records)["jurisdiction"] == "outside-city"
    records["Parcels"]["features"][0] = feature(
        [(0, 0), (10, 10), (0, 10), (10, 0), (0, 0)]
    )
    assert gis.summarize(records)["zoning_status"] == "needs-review"


def test_inputs():
    assert gis.query_filter("2126-037-055") == "AIN='2126037055'"
    assert "O''NEIL" in gis.query_filter("O'Neil")
    for value in ("", "1234", "%", "a" * 161):
        with pytest.raises(ValueError):
            gis.query_filter(value)


@pytest.mark.parametrize(
    "body",
    [
        {"error": {"message": "Unavailable"}},
        {"features": [], "exceededTransferLimit": True},
        {"oops": []},
    ],
)
def test_source_failures(body):
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json=body))
        ) as c:
            result = await gis.query(c, "Parcels", {"where": "1=1"})
            assert result["status"] == "unavailable"

    asyncio.run(run())


def test_no_match_is_not_failure():
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(200, json={"features": []})
            )
        ) as c:
            assert (await gis.query(c, "Parcels", {}))["status"] == "no-match"

    asyncio.run(run())


def test_manual_calculations():
    # Independent examples: 80-ft depth gives 16, 120 gives cap 20.
    assert rules.calculate("front-yard", {"lot_depth_ft": 80})[0] == 16
    assert rules.calculate("front-yard", {"lot_depth_ft": 120})[0] == 20
    assert (
        rules.calculate("side-yard", {"lot_width_ft": 40, "building_height_ft": 18})[0]
        == 4
    )
    assert (
        rules.calculate("side-yard", {"lot_width_ft": 50, "building_height_ft": 28.1})[
            0
        ]
        == 7
    )
    assert rules.calculate("height", {"roof_slope_percent": 24.99})[0] == 28
    assert rules.calculate("height", {"roof_slope_percent": 25})[0] == 33
    assert rules.calculate("floor-area", {"lot_area_sqft": 6000})[0] == 2700
    assert rules.calculate("rear-yard", {})[0] == 15


def test_assessment_unsupported_missing_and_api_contract():
    ctx = gis.summarize(context_records())
    assert (
        rules.assess(ctx, "adu", {}, {}, bundle=([], "test"))["status"] == "unsupported"
    )
    assert (
        rules.assess(ctx, "single-family", {}, {}, bundle=([], "test"))["status"]
        == "partial"
    )
    with pytest.raises(ValueError):
        rules.assess(ctx, "single-family", {"lot_width_ft": float("nan")}, {})
    c = TestClient(app)
    assert c.post("/api/assessments", json={"snapshot_id": "absent"}).status_code == 410
    assert (
        c.post(
            "/api/assessments", json={"snapshot_id": "absent", "zone": "R1-1"}
        ).status_code
        == 422
    )
    SNAPSHOTS["expired"] = (time.monotonic() - 901, ctx)
    assert (
        c.post("/api/assessments", json={"snapshot_id": "expired"}).status_code == 410
    )


def test_timeout_and_body_limit():
    async def run():
        def timeout(request):
            raise httpx.ReadTimeout("source deadline")

        async with httpx.AsyncClient(transport=httpx.MockTransport(timeout)) as c:
            start = time.monotonic()
            r = await gis.query(c, "Parcels", {})
            assert r["status"] == "unavailable" and time.monotonic() - start < 30
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(200, content=b"x" * 16_000_001)
            )
        ) as c:
            assert "size limit" in (await gis.query(c, "Parcels", {}))["error"]

    asyncio.run(run())


def test_boundary_touch_gap_and_multiregime():
    records = context_records()
    records["Chapter 1 zoning"]["features"].append(
        feature(
            [(10, 0), (11, 0), (11, 10), (10, 10), (10, 0)], {"ZONE_CMPLT": "RD5-1"}
        )
    )
    r = gis.summarize(records)
    assert r["zone"] == "R1-1" and r["zone_matches"][1]["boundary_touch"]
    records = context_records()
    records["Chapter 1 zoning"]["features"][0] = feature(
        [(0, 0), (9, 0), (9, 10), (0, 10), (0, 0)], {"ZONE_CMPLT": "R1-1"}
    )
    assert gis.summarize(records)["zoning_status"] == "needs-review"
    records = context_records()
    records["Chapter 1A zoning"].update(
        status="matched",
        features=copy.deepcopy(records["Chapter 1 zoning"]["features"]),
    )
    assert gis.summarize(records)["zoning_status"] == "needs-review"


def test_cache_origin_and_copy_isolation():
    gis.CACHE["1234567890"] = (time.monotonic(), gis.summarize(context_records()))

    async def run():
        r = await gis.context_for("1234567890")
        assert all(v["origin"] == "cached" for v in r["records"].values())
        r["records"]["Parcels"]["features"].clear()
        assert gis.CACHE["1234567890"][1]["records"]["Parcels"]["features"]

    asyncio.run(run())
    gis.CACHE.clear()


def test_partial_source_and_footprint_states():
    records = context_records()
    records["Specific plans"]["status"] = "unavailable"
    result = gis.summarize(records)
    assert result["records"]["Historic overlays"]["status"] == "no-match"
    records["Buildings"].update(status="unavailable", features=[])
    r = gis.summarize(records)
    assert r["map"]["features"] and r["records"]["Buildings"]["status"] == "unavailable"


def test_strict_api_inputs():
    SNAPSHOTS["valid"] = (time.monotonic(), gis.summarize(context_records()))
    c = TestClient(app)
    assert (
        c.post(
            "/api/assessments",
            json={"snapshot_id": "valid", "inputs": {"lot_width_ft": True}},
        ).status_code
        == 422
    )
    assert (
        c.post(
            "/api/assessments",
            json={"snapshot_id": "valid", "checks": {"ordinary_context": "false"}},
        ).status_code
        == 422
    )


def test_multipolygon_and_not_checked():
    from shapely.geometry import MultiPolygon

    records = context_records()
    one = Polygon([(0, 0), (4, 0), (4, 4), (0, 4)])
    two = Polygon([(6, 6), (10, 6), (10, 10), (6, 10)])
    records["Parcels"]["features"][0]["geometry"] = mapping(MultiPolygon([one, two]))
    assert gis.summarize(records)["estimated_area_sqft"] == 32

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(200, json={"features": []})
            )
        ) as client:
            ctx = await gis.context_for("0000000000", client, False)
            assert ctx["records"]["Specific plans"]["status"] == "not-checked"

    asyncio.run(run())


@pytest.mark.parametrize("body", [[], None, {"features": [{}]}])
def test_malformed_upstream(body):
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(200, content=json.dumps(body))
            )
        ) as client:
            assert (await gis.query(client, "Parcels", {}))["status"] == "unavailable"

    asyncio.run(run())


def test_full_address_normalization_and_house_filter():
    query = gis.query_filter("7537 Louise Avenue, Los Angeles, CA 91406-1234")
    assert (
        query
        == "SitusHouseNo='7537' AND UPPER(SitusFullAddress) LIKE '%7537 LOUISE AVE LOS ANGELES CA 91406%'"
    )
    assert (
        gis.query_filter("  7537   LOUISE AVE  ")
        == "SitusHouseNo='7537' AND UPPER(SitusFullAddress) LIKE '%7537 LOUISE AVE%'"
    )
