"""Structural V4.9 single-composite and explicit legacy-dual tests; not real PDF regression."""
import copy
import json
import sys
from pathlib import Path

import ezdxf
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from export_dxf import export_job  # noqa: E402


CHECKS = dict.fromkeys(("contour_topology", "datum", "feature_count", "unfold",
                        "containment", "bend_domain", "material_rules", "slot_semantics"), "PASS")


def part(code, size=(30, 20)):
    x, y = size
    return {"code": code, "material": "SS", "thickness_mm": 2,
            "status": "PASS", "checks": dict(CHECKS), "entities": [
                {"type": "LWPOLYLINE", "role": "outer", "closed": True,
                 "vertices": [[0, 0, 0], [x, 0, 0], [x, y, 0], [0, y, 0]]},
                {"type": "CIRCLE", "role": "hole", "center": [x/2, y/2], "radius": 2},
                {"type": "POINT", "role": "ordinary_point", "point": [6, 6]},
                {"type": "POINT", "role": "through_piercing", "color": 3, "point": [12, 6]},
                {"type": "LINE", "role": "bend", "linetype": "DASHED", "start": [5, 0], "end": [5, y]},
                {"type": "LINE", "role": "bend", "linetype": "DASHED", "start": [8, 0], "end": [8, y]},
            ]}


def test_two_part_dxf_and_manifest(tmp_path):
    job = {"job_id": "520924-19", "parts": [part("000001"), part("000002", (40, 15))]}
    manifest = export_job(job, tmp_path, mode="dual")
    assert [p["code"] for p in manifest["parts"]] == ["000001", "000002"]
    assert len(manifest["combined"]["PASS"]["parts"]) == 2
    assert manifest["combined"]["PASS"]["parts"][0]["combined_bbox_mm"][1] >= 25
    assert manifest["combined"]["PASS"]["parts"][1]["combined_bbox_mm"][3] == 15
    for filename, count in [("520924-19_000001.dxf", 6), ("520924-19_000002.dxf", 6), ("520924-19_ALL.dxf", 12)]:
        doc = ezdxf.readfile(tmp_path / filename)
        assert len(list(doc.modelspace())) == count
        assert doc.header["$INSUNITS"] == 4
        assert all(e.dxf.layer == "0" for e in doc.modelspace())
    assert (tmp_path / "520924-19_MANIFEST.json").is_file()
    assert json.loads((tmp_path / "520924-19_MANIFEST.json").read_text())["contract"] == "TrainAiCad-DXF-V4.7"


def test_preview_is_isolated_from_production(tmp_path):
    good = part("000001")
    review = part("000002")
    review.update(status="PREVIEW", flags=["unreadable numeric X"], preview_reason="numeric_only_known_topology")
    review["entities"].append({"type": "POINT", "role": "estimated", "color": 6, "point": [15, 15]})
    review["entities"].append({"type": "TEXT", "role": "estimated_note", "color": 6, "insert": [15, 16], "text": "ESTIMATED - CHECK DRAWING"})
    manifest = export_job({"job_id": "JOB", "parts": [good, review]}, tmp_path, mode="dual")
    assert (tmp_path / "JOB_ALL.dxf").is_file()
    assert (tmp_path / "JOB_PREVIEW_ALL.dxf").is_file()
    assert [p["code"] for p in manifest["combined"]["PASS"]["parts"]] == ["000001"]
    assert [p["code"] for p in manifest["combined"]["PREVIEW"]["parts"]] == ["000002"]
    with pytest.raises(ValueError):
        bad = copy.deepcopy(review)
        bad["entities"] = bad["entities"][:-1]
        export_job({"job_id": "JOB", "parts": [bad]}, tmp_path, mode="dual")


def test_rejects_unvalidated_or_wrong_layers(tmp_path):
    good = part("000001")
    del good["checks"]["datum"]
    with pytest.raises(ValueError, match="eight upstream"):
        export_job({"job_id": "JOB", "parts": [good]}, tmp_path, mode="dual")
    good = part("000001")
    good["entities"][1]["layer"] = "HOLES"
    with pytest.raises(ValueError, match="Layer 0"):
        export_job({"job_id": "JOB", "parts": [good]}, tmp_path, mode="dual")


def test_rejects_magenta_and_wrong_point_semantics(tmp_path):
    good = part("000001")
    good["entities"][2]["color"] = 3
    with pytest.raises(ValueError, match="ordinary POINT"):
        export_job({"job_id": "JOB", "parts": [good]}, tmp_path, mode="dual")
    good = part("000001")
    good["entities"][1]["color"] = 6
    with pytest.raises(ValueError, match="Magenta"):
        export_job({"job_id": "JOB", "parts": [good]}, tmp_path, mode="dual")


def test_stadium_bulges_and_three_primitives_one_approved_style_relief(tmp_path):
    """Synthetic feature serialization, not the 055958 drawing geometry itself."""
    from ezdxf import bbox

    sample = part("000003")
    sample["entities"].extend([
        # Horizontal stadium: W=4.5, C=10, L_TOTAL=14.5. CW interior loop.
        {"type": "LWPOLYLINE", "role": "slot", "closed": True,
         "vertices": [[10, 17.25, 0], [20, 17.25, -1],
                      [20, 12.75, 0], [10, 12.75, -1]]},
        # One connected Green slit, represented by three CAD entities.
        {"type": "LINE", "role": "relief", "color": 3, "start": [24, 2], "end": [25, 2]},
        {"type": "ARC", "role": "relief", "color": 3, "center": [25, 2.5],
         "radius": 0.5, "start_angle": 270, "end_angle": 0},
        {"type": "LINE", "role": "relief", "color": 3,
         "start": [25.5, 2.5], "end": [26, 2.5]},
    ])
    manifest = export_job({"job_id": "SYNTHETIC", "parts": [sample]}, tmp_path, mode="dual")
    doc = ezdxf.readfile(tmp_path / "SYNTHETIC_000003.dxf")
    msp = doc.modelspace()
    assert manifest["parts"][0]["entity_count"] == 10
    slot = [e for e in msp if e.dxftype() == "LWPOLYLINE"][1]
    assert [round(v[2], 6) for v in slot.get_points("xyb")] == [0, -1, 0, -1]
    bounds = bbox.extents([slot])
    assert round(bounds.extmax.x - bounds.extmin.x, 6) == 14.5
    assert round(bounds.extmax.y - bounds.extmin.y, 6) == 4.5
    assert len([e for e in msp if e.dxftype() == "ARC" and e.dxf.color == 3]) == 1
    assert len([e for e in msp if e.dxftype() == "LINE" and e.dxf.color == 3]) == 2
    assert len(list(ezdxf.readfile(tmp_path / "SYNTHETIC_ALL.dxf").modelspace())) == 10


def test_default_one_combined_with_exact_code_labels(tmp_path):
    job = {"job_id": "ONE", "parts": [part("043791"), part("043792", (40, 15))]}
    manifest = export_job(job, tmp_path)
    assert manifest["contract"] == "TrainAiCad-DXF-V4.9"
    assert manifest["filename"] == "ONE_ALL.dxf"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["ONE_ALL.dxf"]
    doc = ezdxf.readfile(tmp_path / "ONE_ALL.dxf")
    geom = [e for e in doc.modelspace() if e.dxf.layer == "0"]
    meta = [e for e in doc.modelspace() if e.dxf.layer == "AI_META"]
    assert len(geom) == 12
    assert [e.dxf.text for e in meta] == ["043791", "043792"]
    assert doc.layers.get("AI_META").dxf.plot == 0
    assert doc.header["$INSUNITS"] == 4
    assert all(e.dxftype() == "TEXT" for e in meta)
    positions = manifest["positions"]
    assert [x["code"] for x in positions] == ["043791", "043792"]
    assert positions[0]["combined_bbox_mm"][1] - positions[1]["combined_bbox_mm"][3] >= 10


def test_one_review_only_with_user_authorized_unknown_diameter_and_source_views(tmp_path):
    a = part("043791")
    b = part("043797")
    b.update(status="PREVIEW", flags=["customer has not given the two diameters"],
             preview_reason="numeric_only_known_topology")
    b["entities"].extend([
        {"type": "CIRCLE", "role": "estimated", "color": 6, "center": [9, 10], "radius": 3.5},
        {"type": "TEXT", "role": "estimated_note", "color": 6,
         "text": "2-D?", "insert": [9, 13], "height": 2.5},
    ])
    c = {"code": "043796", "material": "SS", "thickness_mm": 3.2,
         "status": "VIEWS_ONLY", "preview_reason": "separate_source_views",
         "flags": ["Z-fold length absent from customer PDF"],
         "checks": {**CHECKS, "unfold": "FLAGGED", "bend_domain": "FLAGGED"},
         "entities": [
             {"type": "LINE", "role": "source_view", "view_id": "FRONT",
              "start": [0, 0], "end": [20, 0]},
             {"type": "LINE", "role": "source_view", "view_id": "SIDE",
              "start": [35, 0], "end": [35, 25]},
         ]}
    manifest = export_job({"job_id": "MIXED", "parts": [a, b, c]}, tmp_path)
    assert manifest["status"] == "REVIEW_ONLY"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["MIXED_ALL_REVIEW_ONLY.dxf"]
    assert not (tmp_path / "MIXED_ALL.dxf").exists()
    doc = ezdxf.readfile(tmp_path / manifest["filename"])
    meta = [e.dxf.text for e in doc.modelspace() if e.dxf.layer == "AI_META"]
    assert meta.index("043791") < meta.index("043797 [FLAG]") < meta.index("043796 [VIEWS_ONLY - FLAG]")
    assert "043796 VIEW FRONT" in meta and "043796 VIEW SIDE" in meta
    assert "REVIEW ONLY - NO CUT - UNRESOLVED CODES PRESENT" in meta
    geometry = [e for e in doc.modelspace() if e.dxf.layer == "0"]
    assert any(e.dxftype() == "CIRCLE" and e.dxf.get("color", 256) == 6 for e in geometry)
    assert len([e for e in geometry if e.dxftype() == "LINE" and e.dxf.get("linetype") != "DASHED"]) == 2


def test_source_views_need_explicit_ids_and_separation(tmp_path):
    p = {"code": "Z", "material": "SS", "thickness_mm": 3.2,
         "status": "VIEWS_ONLY", "preview_reason": "separate_source_views",
         "flags": ["not a full unfold"], "checks": {**CHECKS, "unfold": "FLAGGED"},
         "entities": [
             {"type": "LINE", "role": "source_view", "view_id": "A",
              "start": [0, 0], "end": [20, 0]},
             {"type": "LINE", "role": "source_view", "view_id": "B",
              "start": [25, 0], "end": [35, 0]},
         ]}
    with pytest.raises(ValueError, match="separated"):
        export_job({"job_id": "J", "parts": [p]}, tmp_path)
    p["entities"][1]["view_id"] = ""
    with pytest.raises(ValueError, match="job_id/code"):
        export_job({"job_id": "J", "parts": [p]}, tmp_path)


def test_manifest_only_when_requested(tmp_path):
    manifest = export_job({"job_id": "EX", "parts": [part("P1")]},
                          tmp_path, write_manifest=True)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["EX_ALL.dxf", "EX_MANIFEST.json"]
    assert json.loads((tmp_path / "EX_MANIFEST.json").read_text())["filename"] == manifest["filename"]
