"""V4.34 521013-21 semantic negative gates and single DXF pose regression."""
import copy
import math
import sys
from pathlib import Path

import ezdxf
import pytest
from ezdxf import bbox

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from canonical_contract import CanonicalContractError, validate_canonical_job
from dimension_witness import WitnessError, validate_graph
from material_resolver import MaterialResolveError, is_hairline, resolve_material
from slot_anchor import SlotAnchorError, slot_midpoint, validate_slot_anchor
from export_canonical_dxf import export_canonical_job
from export_dxf import CHECKS


def source_group(code, family="OUTER", member="M_OUTER"):
    return {
        "group_id": "G_" + member,
        "family": family,
        "status": "PROVED",
        "source_quantity": 1,
        "members": [{"member_id": member, "status": "PROVED"}],
    }


def model(code="A", width=12, height=40, material="SS", grain=None):
    entity_id = "E_" + code + "_OUTER"
    part = {
        "code": code, "material": material, "thickness_mm": 1.6,
        "status": "PASS", "checks": {key: "PASS" for key in CHECKS}, "flags": [],
        "entities": [{"entity_id": entity_id, "type": "LWPOLYLINE", "role": "outer",
                      "closed": True, "vertices": [[0,0,0],[width,0,0],
                                                    [width,height,0],[0,height,0]]}],
        "source_groups": [source_group(code)],
        "canonical_members": [{
            "canonical_member_id": "CM_" + code, "origin": "SOURCE",
            "source_member_id": "M_OUTER", "group_id": "G_M_OUTER",
            "status": "PROVED", "entity_ids": [entity_id],
        }],
    }
    if grain is not None:
        part["grain"] = grain
    return part


def job(part, version="TrainAiCad-CANONICAL-V4.31"):
    return {"canonical_contract": version, "job_id": "QA_V434", "parts": [part]}


def test_excel_material_aliases_and_process_split():
    cases = [
        ("SECC", "SS"), ("ボンデ", "SS"), ("SECC-P", "SS"),
        ("SPCC", "SS"), ("SPHC", "SS"), ("SS400", "SS"),
        ("SUS304 HL", "SUS"), ("A5052", "AL"), ("銅", "CU_BRASS"),
    ]
    for name, group in cases:
        assert resolve_material(name)["material_family"] == group
    assert resolve_material("ボンデ")["source_cell"].endswith("A32")
    assert resolve_material("SECC=ボンデ")["material_family"] == "SS"
    assert resolve_material("SUS430", "NOBI")["process_group"] == "SS_SUS430_BRASS"
    assert resolve_material("SUS430", "LASER_R")["process_group"] == "SUS"
    assert is_hairline("SUS304 HL")
    with pytest.raises(MaterialResolveError):
        resolve_material("HL")


def chain(wrong=False):
    end = "EDGE_R" if wrong else "HOLE_R"
    return {
        "nodes": {"EDGE_R":"OUTER_EDGE", "HOLE_R":"HOLE_CENTER",
                  "DIAMOND_R":"HOLE_CENTER"},
        "edges": [
            {"from_node":"EDGE_R","to_node":"HOLE_R","axis":"X","kind":"LOCAL",
             "value_mm":-10,"proof":{"pdf_page":3,"evidence_ref":"p3:right-hole",
                    "endpoint_verified":True,"from_type":"OUTER_EDGE","to_type":"HOLE_CENTER"}},
            {"from_node":end,"to_node":"DIAMOND_R","axis":"X","kind":"CHAIN",
             "value_mm":-265,"proof":{"pdf_page":3,"evidence_ref":"p3:dim265",
                    "endpoint_verified":True,"from_type":"OUTER_EDGE" if wrong else "HOLE_CENTER",
                    "to_type":"HOLE_CENTER"}},
        ],
        "targets":[{"feature_id":"M_4HOLES","datum_node":"EDGE_R",
                    "feature_node":"DIAMOND_R","axis":"X","coordinate_mm":-275}],
    }


def test_059759_dim265_uses_hole_center_not_outer_edge():
    assert validate_graph(chain())[("M_4HOLES","X")] == -275
    with pytest.raises(WitnessError, match="DIMENSION_CHAIN_MISMATCH"):
        validate_graph(chain(wrong=True))


def test_witness_endpoint_proof_is_required():
    bad = chain()
    bad["edges"][0]["proof"]["endpoint_verified"] = False
    with pytest.raises(WitnessError, match="WITNESS_ENDPOINT_UNPROVED"):
        validate_graph(bad)


def test_059761_to_059764_slot_midpoint_is_not_end_arc_center():
    rec = {
        "slot_id":"S1","entity_id":"E_SLOT", "source_pdf_page":5,
        "evidence_ref":"p5:dim32", "witness_verified":True,
        "anchor_point":[0,32], "anchor_type":"SLOT_MIDPOINT",
        "axis_unit":[0,1], "width_mm":6.6, "center_distance_mm":7.5,
        "overall_length_mm":14.1, "canonical_midpoint":[0,32],
    }
    assert validate_slot_anchor(rec) == (0,32)
    rec["anchor_type"] = "ARC_CENTER_1"
    with pytest.raises(SlotAnchorError, match="SLOT_ANCHOR_MISMATCH"):
        validate_slot_anchor(rec)
    assert slot_midpoint([0,32], "ARC_CENTER_1", [0,1], 6.6, 7.5) == (0,35.75)
    assert slot_midpoint([0,32], "OUTER_TIP_1", [0,1], 6.6, 7.5) == (0,39.05)


def test_v434_blocks_missing_hole_witness_while_v431_works():
    part = model()
    hole = {"entity_id":"E_HOLE", "type":"CIRCLE", "role":"hole",
            "center":[10,20], "radius":3.3}
    part["entities"].append(hole)
    part["source_groups"].append(source_group("A", family="HOLE", member="M_HOLE"))
    part["canonical_members"].append({
        "canonical_member_id":"CM_HOLE", "origin":"SOURCE",
        "source_member_id":"M_HOLE", "group_id":"G_M_HOLE",
        "status":"PROVED", "entity_ids":["E_HOLE"],
    })
    validate_canonical_job(job(part))
    with pytest.raises(CanonicalContractError, match="WITNESS_REQUIRED_FEATURE_MISSING"):
        validate_canonical_job(job(part, "TrainAiCad-CANONICAL-V4.34"))
    # A real source witness and X/Y coordinates are mandatory for V4.34 HOLE.
    part["witness_required_feature_ids"] = ["M_HOLE"]
    part["feature_witness_graph"] = chain()
    with pytest.raises(CanonicalContractError, match="WITNESS_CANONICAL_ENTITY_LINK_MISSING"):
        part["feature_witness_graph"]["targets"][0]["feature_id"] = "M_HOLE"
        validate_canonical_job(job(part, "TrainAiCad-CANONICAL-V4.34"))


def test_cut_x_long_y_short_and_xdata_readback(tmp_path):
    part = model(width=12, height=40)
    result = export_canonical_job(job(part), tmp_path)
    cut = tmp_path / "parts_dxf/A.dxf"
    assert cut.exists()
    doc = ezdxf.readfile(cut)
    ext = bbox.extents(doc.modelspace(), fast=False)
    assert ext.extmax.x-ext.extmin.x >= ext.extmax.y-ext.extmin.y
    assert result["artifacts"]["parts"][0]["orientation"]["rotation_deg"] == 90
    assert {ent.dxftype() for ent in doc.modelspace()} <= {"LINE","ARC","CIRCLE"}
    assert all(ent.get_xdata("TRAINAICAD") for ent in doc.modelspace())


def test_hl_proof_takes_priority_over_x_long(tmp_path):
    part = model(width=12, height=40, material="SUS304 HL",
                 grain={"is_hl":True,"direction_xy":[1,0],"evidence_ref":"PDF:grain-arrow"})
    result = export_canonical_job(job(part, "TrainAiCad-CANONICAL-V4.34"), tmp_path)
    cut = ezdxf.readfile(tmp_path / "parts_dxf/A.dxf")
    ext = bbox.extents(cut.modelspace(), fast=False)
    assert math.isclose(ext.extmax.x-ext.extmin.x,12,abs_tol=1e-7)
    assert math.isclose(ext.extmax.y-ext.extmin.y,40,abs_tol=1e-7)
    assert result["artifacts"]["parts"][0]["orientation"]["grain_along_x"]


def test_unproved_hl_is_review_not_fake_magenta(tmp_path):
    part = model(material="SUS304 HL", grain={"is_hl":True,"direction_xy":None,
                                              "evidence_ref":None})
    part.update(status="REVIEW", review_reason="HL_DIRECTION_UNPROVED",
                flags=["HL is printed but grain arrow is missing"])
    result = export_canonical_job(job(part, "TrainAiCad-CANONICAL-V4.34"),tmp_path)
    assert result["status"] == "REVIEW_ONLY"
    assert (tmp_path/"QA_V434_ALL_REVIEW_ONLY.dxf").exists()
    assert not list((tmp_path/"parts_dxf").glob("*.dxf"))
    with pytest.raises(CanonicalContractError, match="HL_DIRECTION_UNPROVED"):
        wrong = copy.deepcopy(part)
        wrong.update(status="PASS",flags=[])
        validate_canonical_job(job(wrong, "TrainAiCad-CANONICAL-V4.34"))


def test_composite_only_preserves_json_and_no_parts(tmp_path):
    part = model()
    result = export_canonical_job(job(part), tmp_path, composite_only=True)
    assert result["filename"] == "QA_V434_ALL.dxf"
    assert (tmp_path/"geometry_json/A.json").is_file()
    assert not list((tmp_path/"parts_dxf").glob("*.dxf"))
    assert result["artifacts"]["parts"][0]["cut_readback"] == "COMPOSITE_ONLY"
