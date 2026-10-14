#!/usr/bin/env python3
"""V4.31 521005-05: reject source-member loss before/through DXF serialization."""
from __future__ import annotations

import copy
import math
import sys
import tempfile
from pathlib import Path

import ezdxf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from canonical_contract import CanonicalContractError, validate_canonical_job  # noqa: E402
from export_canonical_dxf import export_canonical_job  # noqa: E402

CHECKS = dict.fromkeys((
    "contour_topology", "datum", "feature_count", "unfold",
    "containment", "bend_domain", "material_rules", "slot_semantics"
), "PASS")


def entity(eid, etype, role, **kwargs):
    return {"entity_id": eid, "type": etype, "role": role, **kwargs}


def source_group(gid, family, mids, status="PROVED", evidence="synthetic regression member ledger"):
    return {
        "group_id": gid, "family": family, "status": status,
        "source_quantity": len(mids), "evidence": evidence,
        "members": [{"member_id": mid, "status": status} for mid in mids],
    }


def cm(mid, gid, eids, status="PROVED"):
    return {
        "canonical_member_id": "CM_" + mid,
        "origin": "SOURCE", "source_member_id": mid,
        "group_id": gid, "status": status, "entity_ids": list(eids),
    }


def outer(code, w, h):
    eid = f"E{code}_OUTER"
    mid = f"M{code}_OUTER"
    return (
        entity(eid, "LWPOLYLINE", "outer", closed=True,
               vertices=[[0, 0, 0], [w, 0, 0], [w, h, 0], [0, h, 0]]),
        source_group(f"G{code}_CUT", "CUT", [mid]),
        cm(mid, f"G{code}_CUT", [eid]),
    )


def part_057862():
    out_ent, out_grp, out_cm = outer("862", 1000, 200)
    ents = [out_ent]
    groups = [out_grp]
    cms = [out_cm]
    specs = [
        ("G862_O9_LEFT", "HOLE", 2, 4.5, 80),
        ("G862_M6", "TAP", 6, 2.5, 220),
        ("G862_O9_MID", "HOLE", 6, 4.5, 500),
        ("G862_O9_RIGHT", "HOLE", 2, 4.5, 860),
    ]
    for gid, family, qty, radius, x0 in specs:
        mids = []
        for i in range(qty):
            mid = f"M_{gid}_{i+1}"
            eid = f"E_{gid}_{i+1}"
            mids.append(mid)
            x = x0 + i * 24
            y = 60 if i % 2 == 0 else 120
            ents.append(entity(eid, "CIRCLE", "hole", center=[x, y], radius=radius))
            cms.append(cm(mid, gid, [eid]))
        groups.append(source_group(gid, family, mids, evidence=f"521005-05 057862 {gid} count regression; coordinates synthetic"))
    return {
        "code": "057862", "material": "SUS", "thickness_mm": 4,
        "status": "PASS", "checks": dict(CHECKS),
        "source_groups": groups, "canonical_members": cms, "entities": ents,
    }


def part_057864():
    out_ent, out_grp, out_cm = outer("864", 220, 120)
    ents = [out_ent]
    groups = [out_grp]
    cms = [out_cm]
    specs = [
        ("G864_O9", "HOLE", 1, 4.5, 25),
        ("G864_O6_A", "HOLE", 2, 3.0, 65),
        ("G864_O6_B", "HOLE", 2, 3.0, 115),
        ("G864_CSK", "HOLE_CSK", 2, 3.5, 165),
    ]
    for gid, family, qty, radius, x0 in specs:
        mids = []
        for i in range(qty):
            mid = f"M_{gid}_{i+1}"
            eid = f"E_{gid}_{i+1}"
            mids.append(mid)
            ents.append(entity(eid, "CIRCLE", "hole", center=[x0 + i*20, 55], radius=radius))
            cms.append(cm(mid, gid, [eid]))
        groups.append(source_group(gid, family, mids, evidence=f"521005-05 057864 proved hole group; coordinates synthetic"))

    r_mids = [f"M_G864_R5_{i+1}" for i in range(8)]
    groups.append(source_group("G864_R5_PENDING", "R", r_mids, status="FLAGGED",
                               evidence="8-R5 customer confirmation pending; keep local FLAG"))
    for mid in r_mids:
        cms.append(cm(mid, "G864_R5_PENDING", [], status="FLAGGED_NO_GEOMETRY"))
    ents.append(entity("E864_FLAG_NOTE", "TEXT", "estimated_note", color=6,
                       insert=[10, 110], text="8-R5 CUSTOMER_CONFIRMATION_PENDING", height=2.5))
    return {
        "code": "057864", "material": "SS", "thickness_mm": 2,
        "status": "PREVIEW", "flags": ["8-R5 CUSTOMER_CONFIRMATION_PENDING"],
        "preview_reason": "numeric_only_known_topology", "checks": dict(CHECKS),
        "source_groups": groups, "canonical_members": cms, "entities": ents,
    }


def part_057873():
    out_ent, out_grp, out_cm = outer("873", 318.64, 108.32)
    ents = [out_ent]
    groups = [out_grp]
    cms = [out_cm]

    tap_mids = [f"M_G873_M8_{i+1}" for i in range(4)]
    groups.append(source_group("G873_M8", "TAP", tap_mids,
                               evidence="2-M8 (opposite side also) => 4 M8; positions synthetic"))
    for i, mid in enumerate(tap_mids):
        eid = f"E_G873_M8_{i+1}"
        ents.append(entity(eid, "CIRCLE", "hole", center=[25 + (i//2)*268, 20 + (i%2)*20], radius=3.4))
        cms.append(cm(mid, "G873_M8", [eid]))

    groups.append(source_group("G873_BEND_LONG", "BEND", ["M_G873_BEND_LONG"],
                               evidence="bend-edge length 248 regression"))
    long_ids = ["E_G873_BEND_LONG_A", "E_G873_BEND_LONG_B"]
    ents.extend([
        entity(long_ids[0], "LINE", "bend", linetype="DASHED", start=[35, 70], end=[283, 70]),
        entity(long_ids[1], "LINE", "bend", linetype="DASHED", start=[35, 72], end=[283, 72]),
    ])
    cms.append(cm("M_G873_BEND_LONG", "G873_BEND_LONG", long_ids))

    end_mids = ["M_G873_BEND_LEFT", "M_G873_BEND_RIGHT"]
    groups.append(source_group("G873_BEND_ENDS", "BEND", end_mids,
                               evidence="two bend-edge lengths 50 regression"))
    for side, x, mid in [("LEFT", 28, end_mids[0]), ("RIGHT", 290, end_mids[1])]:
        ids = [f"E_G873_BEND_{side}_A", f"E_G873_BEND_{side}_B"]
        ents.extend([
            entity(ids[0], "LINE", "bend", linetype="DASHED", start=[x, 5], end=[x, 55]),
            entity(ids[1], "LINE", "bend", linetype="DASHED", start=[x+2, 5], end=[x+2, 55]),
        ])
        cms.append(cm(mid, "G873_BEND_ENDS", ids))

    return {
        "code": "057873", "material": "SS", "thickness_mm": 2,
        "status": "PASS", "checks": dict(CHECKS),
        "source_groups": groups, "canonical_members": cms, "entities": ents,
    }


def build_job():
    return {
        "canonical_contract": "TrainAiCad-CANONICAL-V4.31",
        "job_id": "521005-05-V431",
        "parts": [part_057862(), part_057864(), part_057873()],
    }


def xdata_entity_id(ent):
    tags = ent.get_xdata("TRAINAICAD")
    vals = [t.value for t in tags if t.code == 1000]
    return next(v.split("=", 1)[1] for v in vals if v.startswith("ENTITY_ID="))


def expect_fail(job, token):
    try:
        validate_canonical_job(job)
    except CanonicalContractError as exc:
        assert token in str(exc), str(exc)
    else:
        raise AssertionError(f"expected canonical failure containing {token}")


def main():
    job = build_job()
    validation = validate_canonical_job(job)
    by_code = {p["code"]: p for p in validation["parts"]}
    assert by_code["057862"]["proved_source_member_count"] == 17  # outer + 16 circular operations
    assert by_code["057864"]["proved_source_member_count"] == 8   # outer + 7 proved hole centers
    assert by_code["057873"]["proved_source_member_count"] == 8   # outer + 4 M8 + 3 bends

    # Negative regression: reproduce the old subset behavior and require HARD FAIL.
    bad862 = copy.deepcopy(job)
    p862 = bad862["parts"][0]
    p862["canonical_members"] = [m for m in p862["canonical_members"] if m.get("source_member_id") not in {
        "M_G862_O9_LEFT_2", "M_G862_M6_1", "M_G862_M6_2", "M_G862_M6_3", "M_G862_M6_4", "M_G862_M6_5", "M_G862_M6_6"
    }]
    expect_fail(bad862, "SOURCE_FEATURE_COMPLETENESS_FAIL")

    bad864 = copy.deepcopy(job)
    p864 = bad864["parts"][1]
    keep = {"M864_OUTER", "M_G864_O9_1"} | {f"M_G864_R5_{i+1}" for i in range(8)}
    p864["canonical_members"] = [m for m in p864["canonical_members"] if m.get("source_member_id") in keep]
    expect_fail(bad864, "SOURCE_FEATURE_COMPLETENESS_FAIL")

    bad873 = copy.deepcopy(job)
    p873 = bad873["parts"][2]
    p873["canonical_members"] = [m for m in p873["canonical_members"] if not str(m.get("source_member_id", "")).startswith("M_G873_M8_")]
    expect_fail(bad873, "SOURCE_FEATURE_COMPLETENESS_FAIL")

    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        manifest = export_canonical_job(job, out, write_manifest=True)
        assert manifest["status"] == "REVIEW_ONLY"
        assert manifest["canonical_completeness"]["status"] == "PASS"
        target = out / manifest["filename"]
        doc = ezdxf.readfile(target)
        layer0 = [e for e in doc.modelspace() if e.dxf.layer == "0"]
        ids = [xdata_entity_id(e) for e in layer0]
        assert ids == validation["entity_ids"]

        circles = [(xdata_entity_id(e), round(e.dxf.radius, 4)) for e in layer0 if e.dxftype() == "CIRCLE"]
        assert len([x for x in circles if "G862_" in x[0]]) == 16
        assert len([x for x in circles if "G864_" in x[0]]) == 7
        assert len([x for x in circles if "G873_M8" in x[0]]) == 4

        bend_lines = [e for e in layer0 if e.dxftype() == "LINE" and e.dxf.get("linetype", "") == "DASHED" and "G873_BEND" in xdata_entity_id(e)]
        lengths = sorted(round(math.hypot(e.dxf.end.x-e.dxf.start.x, e.dxf.end.y-e.dxf.start.y), 6) for e in bend_lines)
        assert lengths == [50.0, 50.0, 50.0, 50.0, 248.0, 248.0]
        assert not any(e.dxf.get("color", 256) == 3 and e.dxftype() in {"LINE", "ARC"} for e in layer0 if "873" in xdata_entity_id(e))
        assert (out / "521005-05-V431_MANIFEST.json").is_file()

    print("PASS: V4.31 521005-05 source-member -> canonical -> saved-DXF completeness hard gate")


if __name__ == "__main__":
    main()
