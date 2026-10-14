#!/usr/bin/env python3
import math
import os
import tempfile
from pathlib import Path

import ezdxf

ROOT = Path(os.environ.get("TRAINAICAD_ROOT", Path(__file__).resolve().parents[2]))
B90 = math.tan(math.radians(90.0) / 4.0)


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def radius_from_bulge(p0, p1, bulge):
    c = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    return c * (1.0 + bulge * bulge) / (4.0 * abs(bulge))


def arc_radii(entity):
    return [float(e.dxf.radius) for e in entity.virtual_entities() if e.dxftype() == "ARC"]


entry = (read("AI_ENTRYPOINT.md") + read("docs/RELEASE_INDEX.md"))
router = read("skills/lispcad/router/ROUTER.yaml")
coverage = read("skills/lispcad/router/RULE_COVERAGE.yaml")
ref = read("references/DXF_PHYSICAL_CURVE_DECODING.md")
census = read("skills/lispcad/router/FEATURE_CENSUS.md")
qa = read("regression/qa/521001-19_V4_26_APPROVED.md")
workflow = read(".github/workflows/dxf-export-tests.yml")
current = read("skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md")
v424 = read("skills/lispcad/versions/V4.24/SKILL_LISPCAD_V4_24_PORTABLE.md")

# V4.26 is an immutable historical regression. A later active release may be current,
# so assert retained release wiring rather than pinning the repository head to V4.26.
assert "- **V4.26:**" in entry
assert "V4.26:" in coverage
assert "references/DXF_PHYSICAL_CURVE_DECODING.md" in coverage
assert current == v424
assert current.startswith("# SKILL_LISPCAD V4.24 PORTABLE:")
assert "references/DXF_PHYSICAL_CURVE_DECODING.md" in router
assert "physical_curve_decode_before_feature_census" in router
assert "check_521001_19_v426.py" in workflow

for token in [
    "DXF_PHYSICAL_CURVE_DECODE_BEFORE_CENSUS",
    "POLYLINE_BULGE_IS_ARC",
    "PHYSICAL_CURVE_CENSUS",
    "BULGE_ARC_NOT_CHORD",
    "final-vertex -> first-vertex",
    "057688/113",
    "057689/114",
    "2-R3",
    "2-R1",
]:
    assert token in "\n".join([ref, census, qa])

assert math.isclose(4.0 * math.atan(B90), math.radians(90.0), rel_tol=0.0, abs_tol=1e-12)
assert math.isclose(radius_from_bulge((0.0, 3.0), (3.0, 0.0), B90), 3.0, rel_tol=0.0, abs_tol=1e-12)
assert math.isclose(radius_from_bulge((10.0, 1.0), (11.0, 0.0), B90), 1.0, rel_tol=0.0, abs_tol=1e-12)

with tempfile.TemporaryDirectory() as td:
    source = Path(td) / "v426_bulge_source.dxf"
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4
    msp = doc.modelspace()

    # Old-style POLYLINE / VERTEX group-42 bulges: R3 and R1 quarter arcs.
    old = msp.add_polyline2d([(0, 3), (3, 0), (10, 0), (10, 1), (11, 0)])
    old.vertices[0].dxf.bulge = B90
    old.vertices[3].dxf.bulge = B90

    # Closed LWPOLYLINE whose final vertex owns a bulged closing segment.
    lw = msp.add_lwpolyline([(1, 0, 0), (2, 0, 0), (0, 1, B90)], format="xyb", close=True)

    doc.saveas(source)
    loaded = ezdxf.readfile(source)
    assert not loaded.audit().has_errors
    assert loaded.header["$INSUNITS"] == 4

    old2 = next(e for e in loaded.modelspace() if e.dxftype() == "POLYLINE")
    lw2 = next(e for e in loaded.modelspace() if e.dxftype() == "LWPOLYLINE")

    old_bulges = [float(v.dxf.bulge) for v in old2.vertices]
    assert math.isclose(old_bulges[0], B90, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(old_bulges[3], B90, rel_tol=0.0, abs_tol=1e-12)

    radii = sorted(arc_radii(old2))
    assert len(radii) == 2
    assert math.isclose(radii[0], 1.0, rel_tol=0.0, abs_tol=1e-9)
    assert math.isclose(radii[1], 3.0, rel_tol=0.0, abs_tol=1e-9)

    lw_points = list(lw2.get_points("xyb"))
    assert math.isclose(float(lw_points[-1][2]), B90, rel_tol=0.0, abs_tol=1e-12)
    lw_virtual = list(lw2.virtual_entities())
    assert lw_virtual[-1].dxftype() == "ARC"  # final -> first closing segment decoded
    assert math.isclose(float(lw_virtual[-1].dxf.radius), 1.0, rel_tol=0.0, abs_tol=1e-9)

print("V4.26 521001-19 DXF physical-curve bulge regression PASS")
