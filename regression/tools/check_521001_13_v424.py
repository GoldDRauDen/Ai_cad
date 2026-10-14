#!/usr/bin/env python3
import os
import re
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

ROOT = Path(os.environ.get("TRAINAICAD_ROOT", Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(ROOT / "tools"))
from export_dxf import export_job  # noqa: E402
import ezdxf  # noqa: E402

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def nominal_delta_flags(pdf_m_nominal, data_nominal):
    return abs(Decimal(str(data_nominal)) - Decimal(str(pdf_m_nominal))) >= Decimal("0.1")

def pilot_from_table(m_name):
    txt = read("references/THREAD_PILOT_TABLE.md")
    pat = rf"\| \*\*{re.escape(m_name)}\*\* \|[^\n]*?\|\s*([0-9]+(?:\.[0-9]+)?)\s*\|"
    m = re.search(pat, txt)
    if not m:
        raise AssertionError(f"pilot not found: {m_name}")
    return float(m.group(1))

current = read("skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md")
v424 = read("skills/lispcad/versions/V4.24/SKILL_LISPCAD_V4_24_PORTABLE.md")
v423 = read("skills/lispcad/versions/V4.23/SKILL_LISPCAD_V4_23_PORTABLE.md")
entry = (read("AI_ENTRYPOINT.md") + read("docs/RELEASE_INDEX.md"))
router = read("skills/lispcad/router/ROUTER.yaml")
coverage = read("skills/lispcad/router/RULE_COVERAGE.yaml")
geom = read("references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md")
physical = read("references/DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md")
source = read("references/SOURCE_DATA_CLASSIFICATION.md")
material = read("references/MATERIAL_RULES.md")
holes = read("skills/lispcad/features/HOLES_TAPS.md")
cross = read("skills/lispcad/core/CROSS_FEATURE_VALIDATION.md")
validation = read("skills/lispcad/core/VALIDATION.md")
qa = read("regression/qa/521001-13_V4_24_APPROVED.md")
wf = read(".github/workflows/dxf-export-tests.yml")

assert current == v424
assert current.startswith("# SKILL_LISPCAD V4.24 PORTABLE:")
assert v423.startswith("# SKILL_LISPCAD V4.23 PORTABLE:")
assert "V4.24 direct approval" not in v423
assert "- **V4.24:**" in entry
assert "V4.24:" in coverage
assert "regression/qa/521001-13_V4_24_APPROVED.md" in coverage
assert "references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md" in router
for token in [
    "DATA_MANUFACTURING_CANONICALIZATION", "DATA_AUTO_R_CANONICALIZATION",
    "DATA_TAP_NOMINAL_VALIDATION", "THREAD_NOMINAL_REFERENCE",
    "THREAD_PREHOLE_SOURCE", "DATA_PDF_DIM_DIFF", "check_521001_13_v424.py",
]:
    assert token in "\n".join([current, entry, geom, physical, source, material, holes, cross, validation, qa, wf])

assert pilot_from_table("M4") == 3.3
assert pilot_from_table("M5") == 4.2
assert pilot_from_table("M6") == 5.0
assert pilot_from_table("M8") == 6.8
assert "every proved `M*`" in holes
assert "M6 is not a special case" in current

assert not nominal_delta_flags(6.0, 6.0)
assert not nominal_delta_flags(6.0, 6.09)
assert nominal_delta_flags(6.0, 6.10)
assert nominal_delta_flags(8.0, 7.89)
assert "raw inner Ø5.1" in qa and "Ø5.0" in qa

checks = {k: "PASS" for k in (
    "contour_topology", "datum", "feature_count", "unfold",
    "containment", "bend_domain", "material_rules", "slot_semantics"
)}
part = {
    "code": "TAPM6", "material": "SUS304", "thickness_mm": 3.0,
    "status": "PASS", "checks": checks,
    "entities": [
        {"type": "LWPOLYLINE", "role": "outer", "closed": True,
         "vertices": [[0,0,0],[20,0,0],[20,9.5,0.41421356237309503],[19.5,10,0],[0,10,0]]},
        {"type": "CIRCLE", "role": "hole", "center": [10,5], "radius": 2.5},
    ],
}
with tempfile.TemporaryDirectory() as td:
    manifest = export_job({"job_id": "V424", "parts": [part]}, td)
    path = Path(td) / manifest["filename"]
    doc = ezdxf.readfile(path)
    assert not doc.audit().has_errors
    geom_ents = [e for e in doc.modelspace() if e.dxf.layer == "0"]
    circles = [e for e in geom_ents if e.dxftype() == "CIRCLE"]
    polys = [e for e in geom_ents if e.dxftype() == "LWPOLYLINE"]
    assert len(circles) == 1
    assert round(circles[0].dxf.radius * 2, 6) == 5.0
    assert all(round(e.dxf.radius * 2, 6) != 6.0 for e in circles)
    assert len(polys) == 1 and any(abs(v[2]) > 0 for v in polys[0].get_points("xyb"))
    assert doc.header["$INSUNITS"] == 4

print("V4.24 521001-13 DATA manufacturing canonicalization / universal M* regression PASS")
