import json
import math
from pathlib import Path

import pytest
from shapely.affinity import rotate
from shapely.geometry import Polygon, mapping
from backend import extraction, lot_depth

ROOT = Path(__file__).resolve().parents[2]


def recorded_stagg():
    context = json.loads(
        (ROOT / "data/delivery/2202004010-positive-candidate.json").read_text()
    )
    output = json.loads(
        (ROOT / "data/delivery/2202004010-positive-extraction.json").read_text()
    )["raw"]
    output["frontage"]["confirmed"] = True
    output["boundary"] = {
        "tract": "15254",
        "lot": "10",
        "lot_type": "interior",
        "rear_kind": "opposite-boundary",
        "rear_reason": "The straight opposite boundary is shared with the rear lots 12 and 11; it is not an easement line or a converging gore tip.",
        "edges": [
            dict(
                role=role,
                length_ft=value,
                bearing=bearing,
                printed_mark=str(value),
                reason="Independently read tract 15254 sheet 3, lot 10 boundary and collinear printed bearing.",
                document_index=1,
                page=3,
                region=[0.68, 0.20, 0.94, 0.46],
            )
            for role, value, bearing in [
                ("front", 59.71, "S89°58'21\"W"),
                ("rear", 61.96, "S74°12'01\"E"),
                ("side_a", 171.10, "N00°01'39\"W"),
                ("side_b", 188, "N00°01'32\"W"),
            ]
        ],
    }
    tract = json.loads(
        (ROOT / "data/delivery/stagg-depth/tract-source.json").read_text()
    )
    docs = [{**context["document"], "pages": [1]}, {**tract, "pages": [1, 2, 3]}]
    return context, output, docs


def validate(c, o, docs):
    return extraction.validate_output(o, c, 4, docs)


def test_stagg_independently_read_depth_and_provenance():
    c, o, docs = recorded_stagg()
    result = validate(c, o, docs)
    depth = next(x for x in result["observations"] if x["key"] == "lot_depth_ft")
    assert depth["value"] == 179.55
    assert depth["status"] == "machine-corroborated"
    assert depth["method"] == "derived-midpoint-depth"
    assert len(depth["operands"]) == 4 and len(depth["citations"]) == 3
    assert depth["document_hash"] == docs[1]["content_hash"]
    assert any("differ from GIS" in a for a in depth["assumptions"])
    assert not any(x["key"] == "lot_width_ft" for x in result["observations"])


def test_general_rotated_non_stagg_quad():
    c, o, docs = recorded_stagg()
    c["parcel"].update(
        AIN="1234001002", Assr_Map="1234-001", LegalDescription="TRACT # 456 LOT 17"
    )
    o["identity"].update(map_id="1234-001", tract="456", lot="17", parcel_number="2")
    o["observations"] = []
    o["boundary"].update(tract="456", lot="17")
    o["frontage"]["compass"] = "east"
    for e, value, b in zip(
        o["boundary"]["edges"],
        [60, math.hypot(60, 12), 120, 132],
        ["N00°00'00\"E", "N11°18'35.76\"W", "N90°00'00\"E", "N90°00'00\"E"],
    ):
        e.update(length_ft=value, printed_mark=str(value), bearing=b)
    poly = rotate(Polygon([(0, 0), (60, 0), (60, -132), (0, -120)]), -90, origin=(0, 0))
    c["records"]["Parcels"]["features"][0]["geometry"] = mapping(poly)
    result = validate(c, o, docs)
    assert result["observations"][0]["value"] == 126
    assert not result["rejected"]


@pytest.mark.parametrize(
    "change,reason",
    [
        ("corner", "Corner"),
        ("gore", "gore"),
        ("unconfirmed", "confirmed"),
        ("wronglot", "identity"),
        ("diverging", "Side bearings"),
        ("curve", "quadrilateral"),
        ("holes", "without holes"),
        ("wronglength", "conflict"),
        ("badbearing", "bearing"),
        ("notprinted", "printed marking"),
        ("wrongpage", "page"),
        ("wrongdoc", "recorded-map"),
        ("badunits", "EPSG"),
        ("wrongcity", "Chapter 1"),
        ("closure", "close"),
        ("conflict", "Conflicting"),
        ("nan", "bounds"),
        ("badregion", "crop"),
    ],
)
def test_rejects_unsupported_or_conflicting_depth_preserving_area(change, reason):
    c, o, docs = recorded_stagg()
    b = o["boundary"]
    e = b["edges"]
    if change == "corner":
        b["lot_type"] = "corner"
    if change == "gore":
        b["rear_kind"] = "gore-chord"
    if change == "unconfirmed":
        o["frontage"]["confirmed"] = False
    if change == "wronglot":
        b["lot"] = "11"
    if change == "diverging":
        e[2]["bearing"] = "N10°00'00\"W"
    if change == "curve":
        c["records"]["Parcels"]["features"][0]["geometry"] = mapping(
            Polygon([(0, 0), (50, 0), (55, -20), (50, -180), (0, -180)])
        )
    if change == "holes":
        c["records"]["Parcels"]["features"][0]["geometry"] = mapping(
            Polygon(
                [(0, 0), (60, 0), (60, -180), (0, -180)],
                holes=[[(10, -10), (20, -10), (20, -20), (10, -20)]],
            )
        )
    if change == "wronglength":
        for edge in e:
            edge["length_ft"] *= 2
            edge["printed_mark"] = str(edge["length_ft"])
    if change == "badbearing":
        e[2]["bearing"] = "N00°61'00\"W"
    if change == "notprinted":
        e[2]["printed_mark"] = "120"
    if change == "wrongpage":
        e[0]["page"] = 8
    if change == "wrongdoc":
        e[0]["document_index"] = 0
    if change == "badunits":
        c["records"]["Parcels"]["crs"] = "EPSG:4326"
    if change == "wrongcity":
        c["jurisdiction"] = "Other city"
    if change == "closure":
        e[1].update(length_ft=70, printed_mark="70")
    if change == "conflict":
        o["observations"].append(
            {
                **o["observations"][0],
                "key": "lot_depth_ft",
                "value": 179.55,
                "units": "ft",
            }
        )
    if change == "nan":
        e[2]["length_ft"] = float("nan")
    if change == "badregion":
        e[2]["region"] = [1, 0, 0, 1]
    result = validate(c, o, docs)
    assert not any(x["key"] == "lot_depth_ft" for x in result["observations"])
    assert reason.lower() in str(result["rejected"]).lower()
    if change not in ("curve", "holes"):
        assert any(x["key"] == "lot_area_sqft" for x in result["observations"])


def test_source_pin_and_version(monkeypatch, tmp_path):
    c, o, docs = recorded_stagg()
    assert lot_depth.VERSION in extraction.PROMPT
    target = tmp_path / "data/sources/measurement-guidance"
    target.mkdir(parents=True)
    (target / "pins.json").write_text(
        json.dumps([{"path": "changed", "source_hash": "old"}])
    )
    (tmp_path / "changed").write_text("new")
    monkeypatch.setattr(lot_depth, "ROOT", tmp_path)
    result = validate(c, o, docs)
    assert "guidance changed" in str(result["rejected"])


def test_depth_reused_without_clearing_applicability_or_geometry():
    from backend import rules, geometry

    c, o, docs = recorded_stagg()
    extracted = validate(c, o, docs)
    c["automatic_evidence"] = {**extracted, "documents": docs}
    c["machine_observations"] = extracted["observations"]
    result = rules.assess(c, "single-family", {}, {})
    front = next(r for r in result["constraints"] if r["category"] == "front-yard")
    assert front["inputs"]["lot_depth_ft"]["value"] == 179.55
    assert front["inputs"]["lot_depth_ft"]["origin"] == "machine-corroborated"
    assert front["status"] != "evaluated"
    assert geometry.for_assessment(c, result)["status"] == "withheld"
    override = rules.assess(
        c, "single-family", {"lot_depth_ft": 180}, {}, "Explicit design assumption"
    )
    front = next(r for r in override["constraints"] if r["category"] == "front-yard")
    assert front["inputs"]["lot_depth_ft"]["origin"] == "user-supplied"
