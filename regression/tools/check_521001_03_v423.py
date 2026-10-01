#!/usr/bin/env python3
import os
from pathlib import Path
ROOT = Path(os.environ.get("TRAINAICAD_ROOT", Path(__file__).resolve().parents[2]))
def read(rel): return (ROOT / rel).read_text(encoding="utf-8")
def missing_source_physical(src, can, canceled=()): return sorted((set(src)-set(canceled))-set(can))
def extra_canonical_physical(src, can, allowed=()): return sorted(set(can)-(set(src)|set(allowed)))
def pair_matches(a,e,tol=1e-9): return len(a)==len(e) and all(abs(x-y)<=tol for x,y in zip(a,e))
def thickness_residual_signature(a,e,t,tol=1e-9):
    return len(a)==len(e) and all(abs(abs(x-y)-t)<=tol for x,y in zip(a,e))
def normalize_coincident(lines,ndigits=9):
    def c(line):
        a,b=line; a=(round(a[0],ndigits),round(a[1],ndigits)); b=(round(b[0],ndigits),round(b[1],ndigits)); return tuple(sorted((a,b)))
    return sorted(set(c(x) for x in lines))
current=read("skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md")
v423=read("skills/lispcad/versions/V4.23/SKILL_LISPCAD_V4_23_PORTABLE.md")
v422=read("skills/lispcad/versions/V4.22/SKILL_LISPCAD_V4_22_PORTABLE.md")
entry=read("AI_ENTRYPOINT.md"); physical=read("references/DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md")
geom=read("references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md"); mech=read("references/MECHANICAL_CLASSIFIER.md")
face=read("references/FACE_GRAPH_UNFOLD_PROTOCOL.md"); val=read("skills/lispcad/core/VALIDATION.md")
bend=read("skills/lispcad/modes/BEND_UNFOLD.md"); qa=read("regression/qa/521001-03_V4_23_APPROVED.md")
wf=read(".github/workflows/dxf-export-tests.yml")
assert current.startswith("# SKILL_LISPCAD V4.24 PORTABLE:")
assert "V4.23 direct approval / PUSH (2026-10-01)" in current
assert "V4.23 direct approval" not in v422
assert "V4.24 direct approval" not in v423
assert "Current production release is **V4.24**" in entry
assert "check_521001_03_v423.py" in entry and "DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md" in entry
assert "SOURCE_PHYSICAL_TO_CANONICAL" in physical and "CANONICAL_TO_SOURCE_PHYSICAL" in physical
assert "THICKNESS_REPRESENTATION" in geom and "source_entity_census" in mech
assert "PER_BEND_WITNESS_LEDGER" in face and "THICKNESS_SINGLE_USE" in face
assert "BIDIRECTIONAL_SOURCE_CANONICAL_QA" in val and "PER_BEND_WITNESS_LEDGER" in bend
assert "521001-03" in qa and "check_521001_03_v423.py" in wf
s417=["CUT_BASE","R22.5_LEFT","R22.5_RIGHT","HOLE_D32_X2","HOLE_D6_X2","BEND_X2"]
b417=["CUT_BASE","HOLE_D32_X2","HOLE_D6_X2","BEND_X2"]
assert missing_source_physical(s417,b417)==["R22.5_LEFT","R22.5_RIGHT"]
s420=["OUTER_FRAME","INNER_OPENING","HOLES","R_FAMILIES","BEND_X2"]
b420=s420+["THICKNESS_EDGE_LEFT_T6","THICKNESS_EDGE_RIGHT_T6"]
assert extra_canonical_physical(s420,b420)==["THICKNESS_EDGE_LEFT_T6","THICKNESS_EDGE_RIGHT_T6"]
pairs={"418b1":(40.16,48.00),"418b2":(67.32,75.16),"419b1":(40.16,48.00),"419b2":(67.32,75.16),"420b1":(55.22,65.00),"420b2":(635.44,645.22),"293b1":(26.22,36.00),"293b2":(101.44,111.22),"293b3":(296.66,306.44),"293b4":(371.88,381.66),"294b1":(96.66,104.50),"294b2":(127.82,135.66)}
for p in pairs.values(): assert pair_matches(p,p)
assert not pair_matches((71.82,79.66),pairs["418b2"]) and thickness_residual_signature((71.82,79.66),pairs["418b2"],4.5)
assert not pair_matches((71.82,79.66),pairs["419b2"]) and thickness_residual_signature((71.82,79.66),pairs["419b2"],4.5)
assert not pair_matches((20.22,30.00),pairs["293b1"]) and thickness_residual_signature((20.22,30.00),pairs["293b1"],6.0)
assert not pair_matches((377.88,387.66),pairs["293b4"]) and thickness_residual_signature((377.88,387.66),pairs["293b4"],6.0)
assert not pair_matches((132.32,140.16),pairs["294b2"]) and thickness_residual_signature((132.32,140.16),pairs["294b2"],4.5)
assert len(normalize_coincident([((0,48),(10,48)),((10,48),(0,48))]))==1 and "REFERENCE_ANOMALY" in qa
print("V4.23 521001-03 physical-census/bidirectional/per-bend regression PASS")
