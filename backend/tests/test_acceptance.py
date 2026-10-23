"""Recorded GIS contexts plus explicitly hypothetical, independently derived inputs."""

import copy
import json
import subprocess
import pytest
from fastapi.testclient import TestClient
from backend import gis, rules, ingest
import backend.app as api

INPUTS = {
    "lot_depth_ft": 80,
    "lot_width_ft": 40,
    "lot_area_sqft": 6000,
    "building_height_ft": 18,
    "roof_slope_percent": 20,
}
CHECKS = {key: True for key in rules.CHECKS}
NOTE = "Hypothetical acceptance scenario; not surveyed dimensions or verified site applicability."


def fixture(ain="2202010009"):
    return json.loads((gis.ROOT / "data/fixtures" / f"{ain}.json").read_text())


@pytest.mark.parametrize(
    "ain,inputs,expected",
    [
        ("2202010009", INPUTS, [16, 4, 15, 28, 2700]),
        (
            "2202010010",
            dict(
                lot_depth_ft=120,
                lot_width_ft=50,
                lot_area_sqft=7500,
                building_height_ft=28.1,
                roof_slope_percent=25,
            ),
            [20, 7, 15, 33, 3375],
        ),
    ],
)
def test_independent_supported_examples(ain, inputs, expected):
    ctx = fixture(ain)
    recomputed = gis.summarize(ctx["records"])
    assert recomputed["zone"] == "R1-1" and recomputed["jurisdiction"] == "Los Angeles"
    result = rules.assess(ctx, "single-family", inputs, CHECKS, NOTE)
    assert result["status"] == "evaluated"
    assert [r["value"] for r in result["constraints"]] == expected
    assert all(
        r["confidence"] == "medium" and r["citations"] and r["rule_version"]
        for r in result["constraints"]
    )
    assert result == rules.assess(ctx, "single-family", inputs, CHECKS, NOTE)


@pytest.mark.parametrize("category", rules.CATEGORIES)
def test_each_rule_withheld_for_unknown_applicability(category):
    result = rules.assess(
        fixture(),
        "single-family",
        INPUTS,
        {**CHECKS, "outside_hillside_coastal": False},
        NOTE,
    )
    r = next(r for r in result["constraints"] if r["category"] == category)
    assert r["status"] == "needs-review" and r["value"] is None


def test_missing_dimensions_and_user_evidence():
    result = rules.assess(fixture(), "single-family", {}, CHECKS, NOTE)
    assert [r["status"] for r in result["constraints"]] == [
        "needs-review",
        "needs-review",
        "evaluated",
        "needs-review",
        "needs-review",
    ]
    assert all(
        r["value"] is None
        for r in rules.assess(fixture(), "single-family", INPUTS, CHECKS)["constraints"]
    )
    for value in (-1, float("inf"), True, "12"):
        with pytest.raises(ValueError):
            rules.assess(
                fixture(), "single-family", {"lot_width_ft": value}, CHECKS, NOTE
            )


def test_verified_evidence_confidence_and_override():
    ctx = fixture()
    ctx["verified_facts"] = {
        k: {
            "value": v,
            "evidence": "Synthetic verified evidence for trust-path test only",
            "verified": True,
            "reviewer": "test",
        }
        for k, v in {**INPUTS, **CHECKS}.items()
    }
    assert all(
        r["confidence"] == "high"
        for r in rules.assess(ctx, "single-family", {}, {})["constraints"]
    )
    result = rules.assess(ctx, "single-family", {"lot_width_ft": 50}, {}, NOTE)
    assert (
        result["constraints"][1]["confidence"] == "medium"
        and result["constraints"][1]["value"] == 5
    )
    ctx["verified_facts"]["lot_width_ft"]["value"] = -1
    with pytest.raises(ValueError):
        rules.assess(ctx, "single-family", {}, {})


@pytest.mark.parametrize("project", ["adu", "guest-house"])
def test_project_packages_keep_context(project):
    ctx = fixture()
    result = rules.assess(ctx, project, INPUTS, CHECKS, NOTE)
    assert (
        result["status"] in ("evaluated", "partial")
        and len(result["constraints"]) >= 2
        and ctx["map"]["features"]
    )


def test_real_rhea_overlay_outside_and_variation():
    rhea = fixture("2126037055")
    r = gis.summarize(rhea["records"])
    assert r["zoning_status"] == "needs-review" and len(r["zone_matches"]) == 2
    assert any(z["possible_sliver"] for z in r["zone_matches"])
    assert all(
        r["value"] is None
        for r in rules.assess(r, "single-family", INPUTS, CHECKS, NOTE)["constraints"]
    )
    ctx = fixture("4103012026")
    assert ctx["records"]["Specific plans"]["status"] == "matched"
    assert (
        rules.assess(ctx, "single-family", INPUTS, CHECKS, NOTE)["status"] == "partial"
    )
    assert (
        rules.assess(fixture("4328021043"), "single-family", INPUTS, CHECKS, NOTE)[
            "status"
        ]
        == "unsupported"
    )
    for changes in ({"regime": "Chapter 1A"}, {"zone": "R1-1-RIO"}):
        assert (
            rules.assess(
                {**fixture(), **changes}, "single-family", INPUTS, CHECKS, NOTE
            )["status"]
            == "unsupported"
        )


def test_fixture_provenance_and_map():
    for ain in ("2202010009", "2202010010", "2126037055", "4103012026", "4328021043"):
        ctx = fixture(ain)
        for record in ctx["records"].values():
            assert (
                record["source_url"].startswith("https://")
                and record["retrieved_at"]
                and record["crs"] == "EPSG:2229"
            )
        assert "2020" in str(ctx["records"]["Buildings"]["vintage"])
        f = next(
            f for f in ctx["map"]["features"] if f["properties"]["kind"] == "parcel"
        )
        bounds = gis.polygon(f).bounds
        assert -119 < bounds[0] < -117 and 33 < bounds[1] < 35


def test_rule_validation_and_review(tmp_path, monkeypatch):
    bundle = json.loads((gis.ROOT / "data/rules/active.json").read_text())
    sources = rules.source_records()
    for mutation in (
        {"quote": "invented passage"},
        {"units": "meters"},
        {"operation": "eval"},
        {"unresolved_references": ["unknown"]},
        {"required_checks": []},
        {"source_versions": {}},
    ):
        with pytest.raises(ValueError):
            rules.validate_rule({**bundle["rules"][0], **mutation}, sources)
    altered = copy.deepcopy(bundle)
    altered["rules"][0]["scope"] = "tampered"
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(altered))
    with pytest.raises(ValueError, match="modified"):
        ingest.activate(p)
    candidate = gis.ROOT / "data/rules/candidates/initial.json"
    with pytest.raises(ValueError):
        ingest.review(candidate, "test", tmp_path / "approved.json")
    assert not (tmp_path / "approved.json").exists()
    root = tmp_path / "repo"
    (root / "data/rules").mkdir(parents=True)
    (root / "data/sources").mkdir()
    (root / "data/rules/active.json").write_text(json.dumps(bundle))
    current = json.loads((gis.ROOT / "data/sources/current.json").read_text())
    current["12.03"] = "new-source"
    (root / "data/sources/current.json").write_text(json.dumps(current))
    monkeypatch.setattr(rules, "ROOT", root)
    monkeypatch.setattr(rules, "source_records", lambda: sources)
    with pytest.raises(ValueError, match="superseded"):
        rules.load_rules()
    assert (gis.ROOT / "data/rules/versions" / f"{bundle['version']}.json").exists()


def test_subscription_and_provider_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "must-not-use")
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "bad")
    assert (
        "ANTHROPIC_API_KEY" not in ingest.subscription_env()
        and "ANTHROPIC_BASE_URL" not in ingest.subscription_env()
    )
    monkeypatch.setattr(
        ingest.subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess(
            a, 0, '{"loggedIn":true,"authMethod":"api_key"}'
        ),
    )
    with pytest.raises(RuntimeError):
        ingest.check_auth(ingest.subscription_env())
    monkeypatch.setattr(ingest, "check_auth", lambda env: None)
    monkeypatch.setattr(
        ingest.subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess(a, 0, '{"result":"not json"}'),
    )
    with pytest.raises(ValueError):
        ingest.extract(tmp_path / "candidate.json")

    def failure(*a, **kw):
        raise subprocess.TimeoutExpired("claude", 240)

    monkeypatch.setattr(ingest.subprocess, "run", failure)
    with pytest.raises(subprocess.TimeoutExpired):
        ingest.extract(tmp_path / "candidate.json")
    assert not (tmp_path / "candidate.json").exists()


def test_api_full_contract(monkeypatch):
    monkeypatch.setattr(api, "FIXTURE_MODE", True)
    client = TestClient(api.app)
    candidates = client.get("/api/parcels", params={"query": "2202-010-009"}).json()
    assert candidates["features"][0]["properties"]["AIN"] == "2202010009"
    assert (
        len(client.get("/api/parcels", params={"query": "LOUISE"}).json()["features"])
        > 1
    )
    assert (
        client.get("/api/parcels", params={"query": "no matching address"}).json()[
            "status"
        ]
        == "no-match"
    )
    ctx = client.get("/api/parcels/2202010009/context").json()
    request = {
        "snapshot_id": ctx["snapshot_id"],
        "inputs": INPUTS,
        "checks": CHECKS,
        "evidence_note": NOTE,
    }
    first = client.post("/api/assessments", json=request).json()
    assert first["status"] == "evaluated"
    assert first == client.post("/api/assessments", json=request).json()
    request["inputs"] = {**INPUTS, "building_height_ft": 28.1}
    assert (
        client.post("/api/assessments", json=request).json()["constraints"][1]["value"]
        == 6
    )
    assert (
        client.post(
            "/api/assessments", json={**request, "verified_facts": {}}
        ).status_code
        == 422
    )
    assert client.get("/api/parcels/not-an-apn/context").status_code == 422


def test_real_chapter_1a_keeps_gap_but_is_unsupported():
    ctx = fixture("5138014112")
    assert ctx["zone_matches"][0]["regime"] == "Chapter 1A"
    assert (
        ctx["zoning_status"] == "needs-review"
    )  # recorded coverage gap is not silently repaired
    assert (
        rules.assess(ctx, "single-family", INPUTS, CHECKS, NOTE)["status"]
        == "unsupported"
    )


def test_refresh_immutable_and_failure_invalidates_old_rules(tmp_path, monkeypatch):
    import httpx

    root = tmp_path / "repo"
    directory = root / "data/sources/regulations"
    directory.mkdir(parents=True)
    sources = rules.source_records()
    current = json.loads((gis.ROOT / "data/sources/current.json").read_text())
    for record in sources.values():
        (directory / f"{record['content_hash']}.json").write_text(json.dumps(record))
    index = root / "data/sources/current.json"
    index.write_text(json.dumps(current))
    previous = copy.deepcopy(sources[current["12.08"]])
    html = (
        '<div id="codecontent">Section 12.08 ' + ("Changed law text. " * 80) + "</div>"
    )
    original_client = httpx.Client
    monkeypatch.setattr(ingest, "ROOT", root)
    monkeypatch.setattr(ingest, "source_records", lambda: sources)
    monkeypatch.setattr(
        ingest.httpx,
        "Client",
        lambda **kw: original_client(
            transport=httpx.MockTransport(lambda r: httpx.Response(200, text=html)),
            **kw,
        ),
    )

    def provider_failed(output):
        raise RuntimeError("Provider unavailable")

    monkeypatch.setattr(ingest, "extract", provider_failed)
    with pytest.raises(RuntimeError, match="Provider unavailable"):
        ingest.snapshot("12.08", tmp_path / "candidate.json")
    assert json.loads(index.read_text())["12.08"] != current["12.08"]
    assert len(list(directory.glob("*.json"))) == len(sources) + 1
    assert (
        json.loads((directory / f"{previous['content_hash']}.json").read_text())
        == previous
    )
    assert not (tmp_path / "candidate.json").exists()


def test_live_failure_does_not_read_fixture(monkeypatch):
    async def failure(ain, **kwargs):
        return {
            "records": {"Parcels": {"status": "unavailable", "origin": "live"}},
            "issues": ["Synthetic source timeout"],
        }

    def forbidden_fixture(ain):
        raise AssertionError("Live mode must never use fixture fallback")

    monkeypatch.setattr(api, "FIXTURE_MODE", False)
    monkeypatch.setattr(api, "context_for", failure)
    monkeypatch.setattr(api, "fixture", forbidden_fixture)
    result = TestClient(api.app).get("/api/parcels/2202010009/context").json()
    assert (
        result["mode"] == "live"
        and result["records"]["Parcels"]["status"] == "unavailable"
    )
