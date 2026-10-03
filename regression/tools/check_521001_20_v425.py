#!/usr/bin/env python3
import math
import os
import re
import tempfile
from decimal import Decimal
from pathlib import Path

import ezdxf

ROOT = Path(os.environ.get("TRAINAICAD_ROOT", Path(__file__).resolve().parents[2]))


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def data_pdf_flags(pdf_value, data_value):
    return abs(Decimal(str(data_value)) - Decimal(str(pdf_value))) >= Decimal("0.1")


def mid_tolerance(nominal, upper, lower):
    return Decimal(str(nominal)) + (Decimal(str(upper)) + Decimal(str(lower))) / Decimal("2")


def pilot_from_table(m_name):
    txt = read("references/THREAD_PILOT_TABLE.md")
    pat = rf"\| \*\*{re.escape(m_name)}\*\* \|[^\n]*?\|\s*([0-9]+(?:\.[0-9]+)?)\s*\|"
    m = re.search(pat, txt)
    if not m:
        raise AssertionError(f"pilot not found: {m_name}")
    return float(m.group(1))


def physical_segments_equal(a, b, tol=1e-12):
    def canon(seg):
        p, q = seg
        p = (round(p[0], 12), round(p[1], 12))
        q = (round(q[0], 12), round(q[1], 12))
        return tuple(sorted((p, q)))
    return sorted(canon(x) for x in a) == sorted(canon(x) for x in b)


entry = read("AI_ENTRYPOINT.md")
router = read("skills/lispcad/router/ROUTER.yaml")
coverage = read("skills/lispcad/router/RULE_COVERAGE.yaml")
contract = read("references/DATA_RAW_TO_MANUFACTURING_CONTRACT.md")
source = read("references/SOURCE_DATA_CLASSIFICATION.md")
preserve = read("references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md")
physical = read("references/DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md")
holes = read("skills/lispcad/features/HOLES_TAPS.md")
qa = read("regression/qa/521001-20_V4_25_APPROVED.md")
workflow = read(".github/workflows/dxf-export-tests.yml")
current = read("skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md")
v424 = read("skills/lispcad/versions/V4.24/SKILL_LISPCAD_V4_24_PORTABLE.md")
v423 = read("skills/lispcad/versions/V4.23/SKILL_LISPCAD_V4_23_PORTABLE.md")

# V4.25 must remain wired after later repo-direct releases are promoted.
assert "- **V4.25:**" in entry
assert "V4.25:" in coverage
assert "references/DATA_RAW_TO_MANUFACTURING_CONTRACT.md" in coverage
assert "references/DATA_RAW_TO_MANUFACTURING_CONTRACT.md" in router
assert current == v424
assert current.startswith("# SKILL_LISPCAD V4.24 PORTABLE:")
assert v423.startswith("# SKILL_LISPCAD V4.23 PORTABLE:")
assert "V4.25" not in v424

for token in [
    "RAW_DATA_SNAPSHOT",
    "PHYSICAL_DATA_BASELINE",
    "SAME_PARAMETER_GATE",
    "MANUFACTURING_CHANGE_LEDGER",
    "UNTOUCHED_DATA_INVARIANCE_CHECK",
    "DATA_PDF_DIM_DIFF",
    "check_521001_20_v425.py",
]:
    assert token in "\n".join([entry, router, coverage, contract, source, preserve, physical, qa, workflow])

assert not data_pdf_flags(855, 855)
assert not data_pdf_flags(600, 600)
assert not data_pdf_flags(60, 60.000709679)
assert not data_pdf_flags(60, 60.099999)
assert data_pdf_flags(60, 60.1)
assert data_pdf_flags(60, 60.100001)

assert mid_tolerance(855, 0, -0.5) == Decimal("854.75")
assert mid_tolerance(600, 0, -0.5) == Decimal("599.75")

assert not data_pdf_flags(5.0, 5.0)
assert pilot_from_table("M5") == 4.2
assert "THREAD_PREHOLE_SOURCE" in physical and "THREAD_PREHOLE_SOURCE" in contract
assert "raw pre-hole" in holes or "raw pre-hole" in contract or "raw pre-hole" in qa
assert "Ø4.134" in qa and "Ø4.2" in qa

# Representation equality is physical, not raw entity-count identity.
line_rect = [((0.0, 0.0), (20.0, 0.0)), ((20.0, 0.0), (20.0, 10.0)),
             ((20.0, 10.0), (0.0, 10.0)), ((0.0, 10.0), (0.0, 0.0))]
poly_rect = [((0.0, 0.0), (20.0, 0.0)), ((20.0, 0.0), (20.0, 10.0)),
             ((20.0, 10.0), (0.0, 10.0)), ((0.0, 10.0), (0.0, 0.0))]
assert physical_segments_equal(line_rect, poly_rect)

# Synthetic saved-DXF read-back: untouched DATA height must not snap to PDF 60.
untouched_h = 60.000709679
with tempfile.TemporaryDirectory() as td:
    target = Path(td) / "v425_52100120_readback.dxf"
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (750, 0), (750, untouched_h), (0, untouched_h)], close=True,
                       dxfattribs={"layer": "0"})
    msp.add_circle((375, 30), 2.1, dxfattribs={"layer": "0"})
    doc.saveas(target)

    loaded = ezdxf.readfile(target)
    assert not loaded.audit().has_errors
    ents = [e for e in loaded.modelspace() if e.dxf.layer == "0"]
    poly = next(e for e in ents if e.dxftype() == "LWPOLYLINE")
    circ = next(e for e in ents if e.dxftype() == "CIRCLE")
    ys = [p[1] for p in poly.get_points("xy")]
    assert math.isclose(max(ys), untouched_h, rel_tol=0.0, abs_tol=1e-9)
    assert not math.isclose(max(ys), 60.0, rel_tol=0.0, abs_tol=1e-6)
    assert math.isclose(circ.dxf.radius * 2, 4.2, rel_tol=0.0, abs_tol=1e-9)
    assert loaded.header["$INSUNITS"] == 4

print("V4.25 521001-20 DATA-first/manufacturing-second regression PASS")
