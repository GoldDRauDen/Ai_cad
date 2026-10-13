"""520925-03 HD1-approved *semantic* regression; NOT a blind PDF-only test.

Compact rectangles are synthetic CUT holders; KEGAKI / bend coordinates and
OD/Nobi assertions are from the user-approved 520925-03 HD1 report. This
checks source-note -> family -> canonical -> saved DXF behavior, not a full
reconstruction or comparison with the unavailable 520925-03_SS.dxf sample.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import ezdxf
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from canonical_contract import CanonicalContractError  # noqa: E402
from export_canonical_dxf import export_canonical_job  # noqa: E402
from holistic_engineering_guard import canonical_job_anomalies  # noqa: E402

CHECKS = dict.fromkeys((
    "contour_topology", "datum", "feature_count", "unfold",
    "containment", "bend_domain", "material_rules", "slot_semantics"
), "PASS")

# Approved regression EXPECTATIONS, never universal construction inputs.
BENDS = {
    "056135": dict(width=70, flat=172.13, od=[121.93, 56.90],
                   nobi=6.70, pair=[115.23, 121.93], domain=[0, 35]),
    "056138": dict(width=100, flat=151.76, od=[108.60, 49.04],
                   nobi=5.88, pair=[102.72, 108.60], domain=[40, 75]),
}
MARKS = {
    "056137": [([15, 0], [15, 35]), ([19.5, 0], [19.5, 35]),
               ([15, 35], [19.5, 35])],
    "056140": [([40, 20.47], [75, 20.47]), ([40, 20.47], [40, 25]),
               ([40, 25], [75, 25])],
    "056142": [([40, 30.49], [75, 30.49]), ([40, 30.49], [40, 35])],
    "056144": [([40, 15.52], [75, 15.52]), ([40, 15.52], [40, 20.04]),
               ([40, 20.04], [75, 20.04])],
}


def _group(part, family, key, eids, evidence):
    code = part["code"]
    gid = f"{code}.{key}"
    mid = f"{gid}.1"
    part["source_groups"].append({
        "group_id": gid, "family": family, "status": "PROVED",
        "source_quantity": 1, "evidence": evidence,
        "members": [{"member_id": mid, "status": "PROVED"}],
    })
    part["canonical_members"].append({
        "canonical_member_id": f"CM.{mid}",
        "origin": "SOURCE", "source_member_id": mid, "group_id": gid,
        "status": "PROVED", "entity_ids": eids,
    })


def _part(code):
    bend = BENDS.get(code)
    w, h = (bend["width"], bend["flat"]) if bend else (75, 35)
    p = {
        "code": code, "material": "SS400", "thickness_mm": 4.5,
        "status": "PASS", "checks": dict(CHECKS), "flags": [],
        "source_groups": [], "canonical_members": [],
        "source_manufacturing_notes": [], "entities": [{
            "entity_id": f"{code}.OUTER", "type": "LWPOLYLINE",
            "role": "outer", "closed": True,
            "vertices": [[0, 0, 0], [w, 0, 0], [w, h, 0], [0, h, 0]],
        }],
    }
    _group(p, "CUT_OUTER", "OUTER", [f"{code}.OUTER"],
           "Synthetic CUT holder, not the full customer contour")
    if bend:
        eids = []
        for n, y in enumerate(bend["pair"], 1):
            eid = f"{code}.BEND_{n}"
            p["entities"].append({
                "entity_id": eid, "type": "LINE", "role": "bend",
                "linetype": "DASHED", "start": [bend["domain"][0], y],
                "end": [bend["domain"][1], y],
            })
            eids.append(eid)
        _group(p, "BEND", "BEND", eids,
               "HD1 outside-envelope construction + handwritten Nobi")
        p["per_bend_witness_ledger"] = [{
            "bend_id": f"{code}.BEND", "source_group_id": f"{code}.BEND",
            "od_actual_mm": bend["od"], "nobi_mm": bend["nobi"],
            "flat_mm": bend["flat"], "bend_pair_mm": bend["pair"],
        }]
        p["source_manufacturing_notes"].append({
            "text": f"handwritten Nobi {bend['nobi']}",
            "resolution": "ROUTED",
        })
    else:
        eids = []
        for n, (a, b) in enumerate(MARKS[code], 1):
            eid = f"{code}.KEGAKI_{n}"
            p["entities"].append({
                "entity_id": eid, "type": "LINE", "role": "kegaki",
                "color": 1, "start": a, "end": b,
            })
            eids.append(eid)
        _group(p, "KEGAKI", "KEGAKI", eids,
               "PDF View X and approved HD1 A/B contact footprint")
        p["source_manufacturing_notes"].append({
            "text": "KEGAKI / ケガキ", "candidate_family": "KEGAKI",
            "scope": "B contact face", "resolution": "ROUTED",
        })
    return p


def _job():
    return {
        "canonical_contract": "TrainAiCad-CANONICAL-V4.31",
        "job_id": "HD1_SEMANTIC_FIXTURE",
        "parts": [_part(code) for code in (*BENDS, *MARKS)],
    }


def test_hd1_approved_semantic_members_and_dxf_readback(tmp_path):
    j = _job()
    assert canonical_job_anomalies(j) == []
    result = export_canonical_job(j, tmp_path)
    assert result["status"] == "PASS"
    assert result["filename"] == "HD1_SEMANTIC_FIXTURE_ALL.dxf"
    dxf = ezdxf.readfile(tmp_path / result["filename"])
    physical = [e for e in dxf.modelspace() if e.dxf.layer == "0"]
    assert sum(e.dxftype() == "LINE" and e.dxf.get("color") == 1
               for e in physical) == 11
    assert sum(e.dxftype() == "LINE" and e.dxf.get("linetype") == "DASHED"
               for e in physical) == 4
    assert len(list((tmp_path / "parts_dxf").glob("*.dxf"))) == 6
    assert len(list((tmp_path / "geometry_json").glob("*.json"))) == 6
    for code in (*BENDS, *MARKS):
        individual = ezdxf.readfile(tmp_path / "parts_dxf" / f"{code}.dxf")
        assert {e.dxftype() for e in individual.modelspace()} <= {
            "LINE", "ARC", "CIRCLE"
        }


def test_b_contact_mark_not_silently_lost(tmp_path):
    j = _job()
    p = next(p for p in j["parts"] if p["code"] == "056142")
    p["source_groups"] = [g for g in p["source_groups"] if g["family"] != "KEGAKI"]
    p["canonical_members"] = [m for m in p["canonical_members"]
                              if "KEGAKI" not in m["group_id"]]
    p["entities"] = [e for e in p["entities"] if e["role"] != "kegaki"]
    # Canonical source↔canonical self-equality is still intact: this is
    # exactly why a note→family gate is needed above it.
    with pytest.raises(CanonicalContractError, match="SOURCE_NOTE_TO_FAMILY_MISSING"):
        export_canonical_job(j, tmp_path)


def test_guess_mark_on_a_conflicts_with_assigned_host():
    j = _job()
    a = next(p for p in j["parts"] if p["code"] == "056135")
    a["source_manufacturing_notes"].append({
        "text": "KEGAKI", "candidate_family": "KEGAKI",
        "scope": "B contact face", "resolution": "ASSIGNED_TO_B_BY_HD1_USER_GUIDE",
        "target_code": "056137",
    })
    assert canonical_job_anomalies(j) == []
    a["entities"].append({
        "entity_id": "056135.WRONG_MARK", "type": "LINE", "role": "kegaki",
        "color": 1, "start": [0, 0], "end": [4.5, 0],
    })
    _group(a, "KEGAKI", "KEGAKI", ["056135.WRONG_MARK"], "unsupported on A")
    assert any("SOURCE_NOTE_HOST_OWNERSHIP_CONFLICT" in e
               for e in canonical_job_anomalies(j))


def test_wrong_host_code_for_mark_is_rejected():
    j = _job()
    a = next(p for p in j["parts"] if p["code"] == "056135")
    a["source_manufacturing_notes"].append({
        "text": "KEGAKI", "target_code": "056138",
        "resolution": "ASSIGNED_TO_OTHER_PART",
    })
    assert any("SOURCE_NOTE_TARGET_FAMILY_MISSING" in e
               for e in canonical_job_anomalies(j))


def test_bend_arithmetic_cannot_be_passed_by_boolean():
    j = _job()
    p = next(p for p in j["parts"] if p["code"] == "056138")
    p["source_exhausted"] = True
    p["holistic_challenge_run"] = True
    p["per_bend_witness_ledger"][0]["nobi_mm"] = 7.76
    assert any("BEND_OD_NOBI_CLOSURE_FAIL" in e
               for e in canonical_job_anomalies(j))


def test_bend_member_pair_not_a_raw_group_total():
    j = _job()
    p = next(p for p in j["parts"] if p["code"] == "056135")
    p["canonical_members"][-1]["entity_ids"] = ["056135.BEND_1"]
    assert any("BEND_PAIR_SOURCE_GROUP_MISMATCH" in e
               for e in canonical_job_anomalies(j))


def test_views_only_cannot_assert_source_exhausted_without_candidates():
    p = {
        "code": "CASE", "status": "VIEWS_ONLY",
        "source_exhausted": True, "holistic_challenge_run": True,
        "source_groups": [], "canonical_members": [], "entities": [],
    }
    assert "CASE:VIEWS_ONLY_SOURCE_EXHAUSTION_UNPROVED" in (
        canonical_job_anomalies({"parts": [p]})
    )
