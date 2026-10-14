#!/usr/bin/env python3
"""V4.29 521005-13 source-instructed custom SLIT regression."""
from math import isclose
from pathlib import Path
import tempfile

import ezdxf
import yaml


def _release_number(value: str) -> int:
    return int(str(value).upper().replace("V4.", ""))


def _line_tuple(entity):
    s = entity.dxf.start
    e = entity.dxf.end
    return (float(s.x), float(s.y), float(e.x), float(e.y))


def test_job_specific_numeric_facts():
    # User-approved handwritten Nobi for 058155/058156.
    nobi = 7.6
    flat = 70.0 + 110.0 + 70.0 - 2.0 * nobi
    assert isclose(flat, 234.8, abs_tol=1e-12)

    bend_pairs = [(62.4, 70.0), (164.8, 172.4)]
    slit_rows = [66.2, 168.6]
    for (a, b), y in zip(bend_pairs, slit_rows):
        assert isclose((a + b) / 2.0, y, abs_tol=1e-12)
        assert isclose(abs(b - a), nobi, abs_tol=1e-12)

    # Regression-only custom slit length; not universal.
    assert isclose(8.0, 8.0, abs_tol=0.0)
    assert not isclose(8.0, 4.5 + 0.2, abs_tol=1e-12)


def test_source_note_rule_wiring():
    root = Path(__file__).resolve().parents[2]
    ref = (root / "references/SOURCE_MANUFACTURING_NOTE_CENSUS.md").read_text(encoding="utf-8")
    census = (root / "skills/lispcad/router/FEATURE_CENSUS.md").read_text(encoding="utf-8")
    slit = (root / "skills/lispcad/features/SLIT_RELIEF.md").read_text(encoding="utf-8")
    cross = (root / "skills/lispcad/core/CROSS_FEATURE_VALIDATION.md").read_text(encoding="utf-8")
    reg = (root / "regression/qa/521005-13_V4_29_APPROVED.md").read_text(encoding="utf-8")

    text = "\n".join([ref, census, slit, cross, reg])
    for token in [
        "SOURCE_MANUFACTURING_NOTE_CENSUS",
        "SOURCE_NOTE_TO_FAMILY",
        "SOURCE_NOTE_FEATURE_COMPLETENESS",
        "CUSTOM_SOURCE_SLIT",
        "custom source-instructed slit",
        "Never hardcode",
        "not a universal",
        "スリット 8",
        "058155",
        "058156",
        "AI_MISREAD",
        "AI_WORKFLOW_ERROR",
    ]:
        assert token in text

    router = yaml.safe_load((root / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    entry = (root / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    coverage = yaml.safe_load((root / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))

    assert _release_number(router["release"]) >= 29
    assert "references/SOURCE_MANUFACTURING_NOTE_CENSUS.md" in router["default_load"]
    assert router["default_load"].index("references/SOURCE_MANUFACTURING_NOTE_CENSUS.md") < router["default_load"].index("skills/lispcad/router/FEATURE_CENSUS.md")
    assert "source_manufacturing_note_census" in router["post_route_checks"]
    assert "- **V4.29:**" in entry
    assert "V4.29" in coverage["release_coverage"]
    assert "regression/tools/check_521005_13_v429.py" in coverage["release_coverage"]["V4.29"]["regression"]


def test_dxf_physical_fixture_readback():
    root = Path(__file__).resolve().parents[2]
    fixture = root / "regression/assets/521005-13/SLIT_FIXTURE.dxf"
    doc = ezdxf.readfile(fixture)
    assert int(doc.header["$INSUNITS"]) == 4

    lines = list(doc.modelspace().query("LINE"))
    assert len(lines) == 6

    slit_lines = []
    bend_lines = []
    for e in lines:
        x1, y1, x2, y2 = _line_tuple(e)
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if isclose(length, 8.0, abs_tol=1e-9):
            slit_lines.append((x1, y1, x2, y2))
        else:
            bend_lines.append((x1, y1, x2, y2))

    assert len(slit_lines) == 2
    assert len(bend_lines) == 4

    expected = [(0.0, 66.2, 8.0, 66.2), (0.0, 168.6, 8.0, 168.6)]
    got = sorted(slit_lines, key=lambda v: v[1])
    for actual, exp in zip(got, expected):
        for a, b in zip(actual, exp):
            assert isclose(a, b, abs_tol=1e-9)

    # No closed slot/rectangle representation in the fixture.
    assert len(doc.modelspace().query("LWPOLYLINE")) == 0
    assert len(doc.modelspace().query("CIRCLE")) == 0

    # Mandatory save/reopen read-back of the actual fixture geometry.
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "roundtrip.dxf"
        doc.saveas(out)
        reopened = ezdxf.readfile(out)
        assert int(reopened.header["$INSUNITS"]) == 4
        assert len(reopened.modelspace().query("LINE")) == 6


def main():
    test_job_specific_numeric_facts()
    test_source_note_rule_wiring()
    test_dxf_physical_fixture_readback()
    print("PASS: 521005-13 V4.29 source-note census, custom slit routing, physical DXF read-back")


if __name__ == "__main__":
    main()
