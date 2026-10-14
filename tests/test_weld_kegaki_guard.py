"""KH851 source-backed weld-site/KEGAKI regression (synthetic geometry only).

The tests demonstrate compulsory completeness. They intentionally do NOT
claim the PDF 521013-12 offsets or sample DXF coordinates are authoritative.
"""
from copy import deepcopy
from pathlib import Path
import sys

import ezdxf
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from canonical_contract import CanonicalContractError, validate_canonical_job
from export_canonical_dxf import export_canonical_job
from resolve_rules import ResolutionError, resolve_rules

CHECKS = dict.fromkeys(("contour_topology", "datum", "feature_count", "unfold",
                        "containment", "bend_domain", "material_rules",
                        "slot_semantics"), "PASS")


def fixture_job(code="059685", customer="851"):
    # Deliberate small synthetic rectangle, NOT a digitization of PDF 521013-12.
    return {
        "canonical_contract": "TrainAiCad-CANONICAL-V4.31", "legacy_fixture": True,
        "job_id": "REGRESSION_KH851_SYNTHETIC",
        "customer_code": customer,
        "parts": [{
            "code": code, "material": "SS", "thickness_mm": 3,
            "status": "PASS", "checks": dict(CHECKS), "flags": [],
            "source_assembly_view_ids": ["PDF_AB_ASSEMBLY"],
            "source_weld_site_ids": ["WELD_AB_1"],
            "weld_site_census": {
                "inspected_assembly_view_ids": ["PDF_AB_ASSEMBLY"],
                "source_evidence": "PDF assembly view read independently before drawing KEGAKI",
                "sites": [{
                    "weld_site_id": "WELD_AB_1", "status": "PROVED",
                    "parent_code": code, "child_part_id": "A",
                    "assembly_view_id": "PDF_AB_ASSEMBLY", "host_face": "B_TOP",
                    "source_evidence": "Synthetic parent and child weld contact in PDF assembly",
                    "weld_required_cue": False, "self_locating": False,
                    "mark_status": "PROVED", "mark_member_ids": ["M_MARK_A"],
                    "datum_evidence": "Synthetic face contact and datum witness identity",
                }]
            },
            "source_groups": [
                {"group_id": "G_OUTER", "family": "CUT", "status": "PROVED",
                 "source_quantity": 1, "evidence": "Synthetic outer contour",
                 "members": [{"member_id": "M_OUTER", "status": "PROVED"}]},
                {"group_id": "G_MARK", "family": "KEGAKI", "status": "PROVED",
                 "source_quantity": 1, "evidence": "Synthetic source-backed weld registration",
                 "members": [{"member_id": "M_MARK_A", "status": "PROVED"}]}
            ],
            "canonical_members": [
                {"canonical_member_id": "CM_OUTER", "origin": "SOURCE",
                 "source_member_id": "M_OUTER", "group_id": "G_OUTER",
                 "status": "PROVED", "entity_ids": ["E_OUTER"]},
                {"canonical_member_id": "CM_MARK_A", "origin": "SOURCE",
                 "source_member_id": "M_MARK_A", "group_id": "G_MARK",
                 "status": "PROVED", "entity_ids": ["E_MARK_A", "E_MARK_B"]},
            ],
            "entities": [
                {"entity_id": "E_OUTER", "type": "LWPOLYLINE", "role": "outer",
                 "closed": True,
                 "vertices": [[0, 0, 0], [40, 0, 0], [40, 20, 0], [0, 20, 0]]},
                {"entity_id": "E_MARK_A", "type": "LINE", "role": "kegaki",
                 "color": 1, "start": [10, 5], "end": [20, 5]},
                {"entity_id": "E_MARK_B", "type": "LINE", "role": "kegaki",
                 "color": 1, "start": [10, 5], "end": [10, 10]},
            ],
        }]
    }


def part_of(job):
    return job["parts"][0]


def test_kh851_weld_requires_kegaki_even_without_explicit_callout():
    job = fixture_job()
    rec = validate_canonical_job(job)
    assert rec["parts"][0]["weld_kegaki_closure"]["required_site_ids"] == ["WELD_AB_1"]
    assert rec["parts"][0]["weld_kegaki_closure"]["status"] == "PASS"


def test_059685_silent_absence_of_weld_census_is_blocked():
    job = fixture_job()
    part_of(job).pop("weld_site_census")
    with pytest.raises(CanonicalContractError, match="weld_site_census required"):
        validate_canonical_job(job)


def test_059685_deleted_source_weld_site_is_blocked():
    job = fixture_job()
    part_of(job)["weld_site_census"]["sites"] = []
    with pytest.raises(CanonicalContractError, match="source WELD_SITE census"):
        validate_canonical_job(job)


def test_059685_unexamined_assembly_view_is_blocked():
    job = fixture_job()
    part_of(job)["weld_site_census"]["inspected_assembly_view_ids"] = []
    with pytest.raises(CanonicalContractError, match="assembly views missing"):
        validate_canonical_job(job)


def test_059685_kegaki_member_not_just_a_line_without_provenance():
    job = fixture_job()
    part_of(job)["source_groups"][1]["family"] = "CUT"
    with pytest.raises(CanonicalContractError, match="not canonical KEGAKI"):
        validate_canonical_job(job)


def test_059685_color_or_geometry_role_cannot_be_cut():
    job = fixture_job()
    part_of(job)["entities"][1]["color"] = 256
    part_of(job)["entities"][1]["role"] = "cutout"
    with pytest.raises(CanonicalContractError, match="RED LINE"):
        validate_canonical_job(job)


def test_059683_pending_14_mm_mark_must_remain_local_review():
    job = fixture_job(code="059683")
    part = part_of(job)
    site = part["weld_site_census"]["sites"][0]
    site["mark_status"] = "FLAGGED"
    site["unresolved_fields"] = ["customer_pending_red_14mm"]
    part["source_groups"][1]["members"][0]["status"] = "FLAGGED"
    part["canonical_members"][1]["status"] = "FLAGGED_NO_GEOMETRY"
    part["canonical_members"][1]["entity_ids"] = []
    part["entities"] = part["entities"][:1]
    part["status"] = "PREVIEW"
    part["flags"] = ["059683: red 14 mm customer confirmation pending"]
    assert validate_canonical_job(job)["parts"][0]["weld_kegaki_closure"]["status"] == "REVIEW"
    part["status"] = "PASS"
    with pytest.raises(CanonicalContractError, match="FLAGGED weld sites cannot have PASS"):
        validate_canonical_job(job)


def test_no_weld_on_inspected_customer_part_requires_explicit_negative_evidence():
    job = fixture_job(code="059677")
    part = part_of(job)
    part["source_weld_site_ids"] = []
    part["weld_site_census"]["sites"] = []
    with pytest.raises(CanonicalContractError, match="no-weld disposition"):
        validate_canonical_job(job)
    part["weld_site_census"]["no_weld_evidence"] = "Source assembly inspected: no contact/weld site for this part"
    assert validate_canonical_job(job)["parts"][0]["weld_kegaki_closure"]["required_site_ids"] == []


def test_non851_does_not_invent_weld_kegaki_for_self_locating_child():
    job = fixture_job(customer="700")
    site = part_of(job)["weld_site_census"]["sites"][0]
    site["self_locating"] = True
    site["not_required_evidence"] = "Proved contact is self-locating without a marking instruction"
    assert validate_canonical_job(job)["parts"][0]["weld_kegaki_closure"]["required_site_ids"] == []


def test_router_blocks_kh851_kegaki_no_and_requires_census():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    census = {
        "part_code": "059685", "customer_code": "851",
        "source_mode": "PDF_ONLY", "part_mode": "FLAT_NO_BEND",
        "reference_present": "NO",
        "features": {name: {"state": "NO"} for name in router["feature_routes"]},
    }
    with pytest.raises(ResolutionError, match="weld_site_census required"):
        resolve_rules(census)
    part = part_of(fixture_job())
    census.update({
        "source_assembly_view_ids": part["source_assembly_view_ids"],
        "source_weld_site_ids": part["source_weld_site_ids"],
        "weld_site_census": part["weld_site_census"]
    })
    with pytest.raises(ResolutionError, match="KEGAKI=NO"):
        resolve_rules(census)
    census["features"]["KEGAKI"]["state"] = "UNKNOWN"
    result = resolve_rules(census)
    assert "KEGAKI" in result["selected_features"]
    assert "skills/lispcad/features/KEGAKI.md" in result["rule_paths"]


def test_canonical_saved_dxf_marks_read_back_with_entity_ids(tmp_path):
    job = fixture_job()
    manifest = export_canonical_job(job, tmp_path)
    doc = ezdxf.readfile(tmp_path / manifest["filename"])
    geom = [e for e in doc.modelspace() if e.dxf.layer == "0"]
    red = [e for e in geom if e.dxftype() == "LINE" and e.dxf.get("color") == 1]
    assert len(red) == 2
    for entity in red:
        assert any(str(tag.value).startswith("ENTITY_ID=")
                   for tag in entity.get_xdata("TRAINAICAD") if tag.code == 1000)
