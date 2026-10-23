import copy
from backend import jobs, questions


def test_cache_reuses_acquisition_but_not_validation_changes(monkeypatch):
    monkeypatch.setattr(jobs, "recover", lambda: None)
    monkeypatch.setattr(jobs, "submit_task", lambda context, key, retry: key)
    context = {
        "parcel": {"AIN": "123", "LegalDescription": "LOT 1"},
        "document": {
            "status": "available",
            "content_hash": "abc",
            "retrieved_at": "old",
        },
        "regime": "Chapter 1",
        "records": {
            "Parcels": {
                "features": [{"geometry": {"type": "Polygon", "coordinates": []}}]
            }
        },
    }
    key = jobs.submit(context)
    changed = copy.deepcopy(context)
    changed["document"]["retrieved_at"] = "new"
    assert jobs.submit(changed) == key
    for field, value in [
        ("regime", "Chapter 1A"),
        ("parcel", {"AIN": "456"}),
        ("records", {}),
        ("document", {"status": "available", "content_hash": "changed"}),
    ]:
        altered = {**context, field: value}
        assert jobs.submit(altered) != key
    monkeypatch.setattr(jobs.lot_depth, "VERSION", "new-validation")
    assert jobs.submit(context) != key


def test_questions_include_saved_map_facts_and_failures(monkeypatch):
    scenario = {
        "assessment": {
            "constraints": [],
            "geometry": {"status": "withheld", "reason": "Irregular lot"},
        },
        "request": {},
        "context": {
            "parcel": {"AIN": "123"},
            "automatic_evidence": {
                "observations": [
                    {
                        "key": "lot_depth_ft",
                        "value": 179.55,
                        "source_url": "https://example.test/map",
                        "assumptions": ["Opposite rear line"],
                    }
                ],
                "uncertainties": ["No width established"],
            },
            "sourced_facts": {
                "existing_primary_dwelling": {
                    "state": "true",
                    "limitation": "Assessor only",
                }
            },
            "records": {
                "Coastal": {
                    "status": "unavailable",
                    "error": "Timed out",
                    "features": ["must not enter prompt"],
                }
            },
        },
    }
    evidence = questions.evidence_for(scenario)
    assert "179.55" in evidence["map-reading-0"]["text"]
    assert "Opposite rear line" in evidence["map-reading-0"]["text"]
    assert "Timed out" in evidence["availability-Coastal"]["text"]
    assert "features" not in evidence["availability-Coastal"]["text"]
    assert "Irregular lot" in evidence["geometry-limitations"]["text"]

    def ask(prompt, **kwargs):
        assert "179.55" in prompt and "Assessor only" in prompt
        return {
            "output": {
                "answer": "The saved map reads 179.55 feet.",
                "insufficient_evidence": False,
                "citations": [{"id": "map-reading-0", "quote": "179.55"}],
            },
            "provenance": {},
        }

    monkeypatch.setattr(questions.model, "ask", ask)
    assert (
        questions.answer(scenario, "What is the depth?")["citations"][0]["evidence"][
            "url"
        ]
        == "https://example.test/map"
    )
    assert "map-reading-0" not in questions.evidence_for(
        {"assessment": {"constraints": []}, "request": {}}
    )


def test_explicit_coastal_conflict_overrides_negative_screen():
    import json
    from backend import rules

    c = json.loads((rules.ROOT / "data/fixtures/2202010009.json").read_text())
    c["records"]["Coastal Zone (state boundary)"] = {"status": "no-match"}
    choices = {
        "existing_primary_dwelling": True,
        "new_detached": True,
        "has_kitchen": True,
    }
    automatic = rules.assess(c, "adu", {}, choices)
    explicit = rules.assess(
        c, "adu", {}, {**choices, "coastal_requirements_resolved": False}
    )
    assert not any("Coastal Act" in r for r in automatic["constraints"][0]["reasons"])
    assert any("Coastal Act" in r for r in explicit["constraints"][0]["reasons"])


def test_cached_result_cannot_attach_to_changed_geometry(monkeypatch):
    import pytest
    from fastapi import HTTPException
    from backend import app

    before = {
        "parcel": {"AIN": "123"},
        "document": {"content_hash": "map"},
        "records": {"Parcels": {"features": [{"geometry": {"coordinates": [1]}}]}},
    }
    after = copy.deepcopy(before)
    after["records"]["Parcels"]["features"][0]["geometry"]["coordinates"] = [2]
    monkeypatch.setattr(app, "snapshot_context", lambda _: after)
    monkeypatch.setattr(
        jobs, "read", lambda _: {"payload": before, "status": "completed"}
    )
    with pytest.raises(HTTPException) as error:
        app.extracted_context("job", app.EvidenceJobRequest(snapshot_id="new"))
    assert error.value.status_code == 409
