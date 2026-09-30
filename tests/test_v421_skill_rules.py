"""V4.21 customer DATA geometry-preservation hard gate."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/"skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE=ROOT/"skills/lispcad/versions/V4.21/SKILL_LISPCAD_V4_21_PORTABLE.md"
BASE=ROOT/"skills/lispcad/versions/V4.20/SKILL_LISPCAD_V4_20_PORTABLE.md"

def test_v421_current_release_and_inheritance():
    entry=(ROOT/"AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    skill=CURRENT.read_text(encoding="utf-8")
    assert "Current production release is **V4.21**" in entry
    assert CURRENT.read_bytes()==RELEASE.read_bytes()
    assert skill.startswith("# SKILL_LISPCAD V4.21 PORTABLE")
    assert BASE.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.20 PORTABLE")
    for token in [
        "PDF_DATA_RAW_GEOMETRY_PRESERVATION.md",
        "520930-03_V4_21_APPROVED.md",
        "DATA_REQUIRED_MISSING",
        "source reprojection",
    ]:
        assert token in (entry + "\n" + skill)

def test_v421_source_classification_hard_gate():
    s=(ROOT/"references/SOURCE_DATA_CLASSIFICATION.md").read_text(encoding="utf-8")
    for token in [
        "DATA geometry must be harvested/preserved",
        "do not redraw",
        "DATA_REQUIRED_MISSING",
        "646",
        "not a redraw tolerance",
    ]:
        assert token in s

def test_v421_reference_and_regression_present():
    ref=(ROOT/"references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md").read_text(encoding="utf-8")
    qa=(ROOT/"regression/qa/520930-03_V4_21_APPROVED.md").read_text(encoding="utf-8")
    assert "every job" in ref
    assert "geometry authority" in ref
    assert "057088 DATA page scale 1:2" in qa
    assert "Same bbox with source-derived internal drift is still FAIL" in qa
