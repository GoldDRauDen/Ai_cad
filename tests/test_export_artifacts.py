"""Per-code JSON and manufacturing-only DXF regression tests (synthetic source)."""
from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

import ezdxf
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from canonical_contract import CanonicalContractError, validate_canonical_job  # noqa: E402
from export_canonical_dxf import export_canonical_job  # noqa: E402
from export_job_artifacts import _arc_from_bulge  # noqa: E402


CHECKS = dict.fromkeys((
    "contour_topology", "datum", "feature_count", "unfold",
    "containment", "bend_domain", "material_rules", "slot_semantics"
), "PASS")


def source_group(code, family, name, eids, state="PROVED", canon_state=None):
    gid = f"G_{code}_{name}"
    mid = f"M_{code}_{name}"
    group = {
        "group_id": gid, "family": family, "status": state,
        "source_quantity": 1,
        "evidence": "synthetic test source claim; not customer dimensions",
        "members": [{"member_id": mid, "status": state}],
    }
    canonical = {
        "canonical_member_id": f"CM_{code}_{name}",
        "origin": "SOURCE", "source_member_id": mid,
        "group_id": gid, "status": canon_state or state, "entity_ids": eids,
    }
    return group, canonical


def part(code, bent=True, slot=True, relief=True):
    entities = [{
        "entity_id": f"E_{code}_OUT", "type": "LWPOLYLINE", "role": "outer",
        "closed": True,
        "vertices": [[0, 0, 0], [40, 0, 0], [40, 30, 0], [0, 30, 0]],
    }, {
        "entity_id": f"E_{code}_HOLE", "type": "CIRCLE",
        "role": "hole", "center": [7, 8], "radius": 2.5,
    }]
    groups, canonical = [], []

    def add(family, name, eids):
        group, member = source_group(code, family, name, eids)
        groups.append(group)
        canonical.append(member)

    add("CUT", "OUT", [f"E_{code}_OUT"])
    add("HOLE", "HOLE", [f"E_{code}_HOLE"])
    if slot:
        # Clockwise interior contour with two analytic negative semicircle bulges.
        entities.append({
            "entity_id": f"E_{code}_SLOT", "type": "LWPOLYLINE",
            "role": "slot", "closed": True,
            "vertices": [[12, 23, 0], [21, 23, -1], [21, 19, 0], [12, 19, -1]],
        })
        add("SLOT", "SLOT", [f"E_{code}_SLOT"])
    if bent:
        ents = []
        for k, x in (("A", 27), ("B", 29)):
            eid = f"E_{code}_BEND_{k}"
            entities.append({
                "entity_id": eid, "type": "LINE", "role": "bend",
                "linetype": "DASHED", "start": [x, 2], "end": [x, 28],
            })
            ents.append(eid)
        add("BEND", "BEND", ents)
    if relief:
        ids = [f"E_{code}_RELIEF_{i}" for i in range(3)]
        entities.extend([
            {"entity_id": ids[0], "type": "LINE", "role": "relief", "color": 3,
             "start": [30, 3], "end": [32, 3]},
            {"entity_id": ids[1], "type": "ARC", "role": "relief", "color": 3,
             "center": [32, 3.5], "radius": .5, "start_angle": 270, "end_angle": 0},
            {"entity_id": ids[2], "type": "LINE", "role": "relief", "color": 3,
             "start": [32.5, 3.5], "end": [33.5, 3.5]},
        ])
        add("RELIEF", "RELIEF", ids)
    return {
        "code": code, "material": "SS", "thickness_mm": 2,
        "status": "PASS", "checks": dict(CHECKS),
        "entities": entities, "source_groups": groups, "canonical_members": canonical,
    }


def review_part(code):
    p = part(code, bent=False, slot=False, relief=False)
    p.update(status="PREVIEW", preview_reason="numeric_only_known_topology",
             flags=["customer confirmation pending"])
    eid = f"E_{code}_FLAG"
    p["entities"].extend([
        {"entity_id": eid, "type": "CIRCLE", "role": "estimated",
         "color": 6, "center": [27, 20], "radius": 2.25},
        {"entity_id": f"E_{code}_FLAG_NOTE", "type": "TEXT", "role": "estimated_note",
         "color": 6, "text": "CHECK DIAMETER", "insert": [27, 25]},
    ])
    g, c = source_group(code, "HOLE", "PENDING", [eid],
                        state="FLAGGED", canon_state="PREVIEW")
    p["source_groups"].append(g)
    p["canonical_members"].append(c)
    return p


def job(parts):
    return {
        "canonical_contract": "TrainAiCad-CANONICAL-V4.31",
        "job_id": "TESTJOB", "parts": parts,
    }


def _xdata(ent):
    return [x.value for x in ent.get_xdata("TRAINAICAD") if x.code == 1000]


def test_pass_and_review_export_separation(tmp_path):
    a, b, r = part("A"), part("B", bent=False, slot=False, relief=False), review_part("REVIEW")
    src = job([a, r, b])
    assert validate_canonical_job(src)["contract"] == src["canonical_contract"]
    result = export_canonical_job(src, tmp_path, write_manifest=True)
    assert result["filename"] == "TESTJOB_ALL_REVIEW_ONLY.dxf"
    assert set(x.name for x in (tmp_path / "geometry_json").glob("*.json")) == {
        "A.json", "REVIEW.json", "B.json",
    }
    assert set(x.name for x in (tmp_path / "parts_dxf").glob("*.dxf")) == {"A.dxf", "B.dxf"}
    assert not (tmp_path / "TESTJOB_ALL.dxf").exists()
    assert (tmp_path / result["filename"]).is_file()
    assert result["artifacts"]["parts"][1]["cut_dxf"] is None
    assert result["artifacts"]["parts"][1]["cut_readback"] == "NOT_PRODUCTION"
    for part_json in (tmp_path / "geometry_json").glob("*.json"):
        loaded = json.loads(part_json.read_text())
        assert loaded["canonical_contract"] == "TrainAiCad-CANONICAL-V4.31"
        assert validate_canonical_job(loaded)["parts"][0]["source_group_count"] > 0
        assert loaded["parts"][0]["code"] == part_json.stem
    for cut in (tmp_path / "parts_dxf").glob("*.dxf"):
        d = ezdxf.readfile(cut)
        ents = list(d.modelspace())
        assert ents
        assert {e.dxftype() for e in ents} <= {"LINE", "ARC", "CIRCLE"}
        assert all(e.dxf.layer == "0" for e in ents)
        assert all(e.dxf.get("color", 256) != 6 for e in ents)
        assert all(any(v.startswith("SOURCE_ENTITY_ID=") for v in _xdata(e)) for e in ents)
    # Outline 4 lines, hole circle, slot 2 lines+2 arcs, relief 2 lines+1 arc.
    types = [e.dxftype() for e in ezdxf.readfile(tmp_path / "parts_dxf/A.dxf").modelspace()]
    assert types.count("LINE") == 8 and types.count("ARC") == 3 and types.count("CIRCLE") == 1
    assert len(types) == 12
    composite = ezdxf.readfile(tmp_path / result["filename"])
    assert "LWPOLYLINE" in [e.dxftype() for e in composite.modelspace()]
    assert any("NO CUT" in e.dxf.text for e in composite.modelspace() if e.dxftype() == "TEXT")


def test_all_pass_total_name_and_unchanged_part_cache(tmp_path):
    src = job([part("A"), part("B", bent=False)])
    r1 = export_canonical_job(src, tmp_path)
    assert r1["filename"] == "TESTJOB_ALL.dxf"
    before_json = (tmp_path / "geometry_json/B.json").stat().st_mtime_ns
    before_cut = (tmp_path / "parts_dxf/B.dxf").stat().st_mtime_ns
    r2 = export_canonical_job(src, tmp_path)
    assert all(p["reused_verified_dxf"] for p in r2["artifacts"]["parts"])
    assert not any(p["json_changed"] for p in r2["artifacts"]["parts"])
    src["parts"][0]["entities"][1]["center"] = [8, 8]
    r3 = export_canonical_job(src, tmp_path)
    assert r3["artifacts"]["parts"][0]["json_changed"]
    assert not r3["artifacts"]["parts"][0]["reused_verified_dxf"]
    assert r3["artifacts"]["parts"][1]["reused_verified_dxf"]
    assert (tmp_path / "geometry_json/B.json").stat().st_mtime_ns == before_json
    assert (tmp_path / "parts_dxf/B.dxf").stat().st_mtime_ns == before_cut


def test_status_downgrade_removes_stale_pass_cut(tmp_path):
    src = job([part("A"), part("B", bent=False)])
    export_canonical_job(src, tmp_path)
    src["parts"][1] = review_part("B")
    result = export_canonical_job(src, tmp_path)
    assert result["filename"] == "TESTJOB_ALL_REVIEW_ONLY.dxf"
    assert not (tmp_path / "parts_dxf/B.dxf").exists()
    assert (tmp_path / "parts_dxf/A.dxf").exists()
    assert json.loads((tmp_path / "geometry_json/B.json").read_text())["parts"][0]["status"] == "PREVIEW"


@pytest.mark.parametrize("start,end,bulge", [
    ((0, 0), (10, 0), 1),
    ((0, 0), (10, 0), -1),
    ((0, 0), (10, 0), 0.5),
    ((0, 0), (10, 0), -2),
])
def test_bulge_arc_preserves_true_analytic_endpoints_and_sweep(start, end, bulge):
    center, radius, sa, ea = _arc_from_bulge(start, end, bulge)
    assert math.isclose((ea - sa) % 360, abs(math.degrees(4 * math.atan(bulge))), abs_tol=1e-6)
    def xy(angle):
        a = math.radians(angle)
        return center[0] + radius * math.cos(a), center[1] + radius * math.sin(a)
    expect = (start, end) if bulge > 0 else (end, start)
    for actual, target in zip((xy(sa), xy(ea)), expect):
        assert math.dist(actual, target) < 1e-6


def test_unclassified_potential_cut_does_not_disappear_silently(tmp_path):
    src = job([part("A")])
    extra = {"entity_id": "E_A_STRANGE", "type": "LINE",
             "role": "unknown_cut_family", "start": [2, 2], "end": [3, 2]}
    src["parts"][0]["entities"].append(extra)
    g, c = source_group("A", "UNKNOWN", "STRANGE", [extra["entity_id"]])
    src["parts"][0]["source_groups"].append(g)
    src["parts"][0]["canonical_members"].append(c)
    with pytest.raises(CanonicalContractError, match="unclassified entity role"):
        export_canonical_job(src, tmp_path)


def test_corrupt_pass_dxf_is_regenerated_after_read_back(tmp_path):
    src = job([part("A")])
    export_canonical_job(src, tmp_path)
    cut = tmp_path / "parts_dxf/A.dxf"
    cut.write_bytes(b"definitely not a DXF")
    output = export_canonical_job(src, tmp_path)
    assert not output["artifacts"]["parts"][0]["reused_verified_dxf"]
    assert ezdxf.readfile(cut).audit().has_errors is False
