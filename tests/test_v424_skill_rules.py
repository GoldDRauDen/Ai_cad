"""V4.24 DATA manufacturing canonicalization and universal M* nominal validation."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE = ROOT / "skills/lispcad/versions/V4.24/SKILL_LISPCAD_V4_24_PORTABLE.md"
PREV = ROOT / "skills/lispcad/versions/V4.23/SKILL_LISPCAD_V4_23_PORTABLE.md"

def test_v424_current_release_and_immutable_v423():
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    skill = CURRENT.read_text(encoding="utf-8")
    assert "Current production release is **V4.24**" in entry
    assert CURRENT.read_bytes() == RELEASE.read_bytes()
    assert skill.startswith("# SKILL_LISPCAD V4.24 PORTABLE")
    assert PREV.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.23 PORTABLE")
    assert "V4.24 direct approval" not in PREV.read_text(encoding="utf-8")

def test_v424_rule_wiring():
    paths = [
        "references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md",
        "references/DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md",
        "references/SOURCE_DATA_CLASSIFICATION.md",
        "references/MATERIAL_RULES.md",
        "skills/lispcad/features/HOLES_TAPS.md",
        "skills/lispcad/core/CROSS_FEATURE_VALIDATION.md",
        "skills/lispcad/core/VALIDATION.md",
        "regression/qa/521001-13_V4_24_APPROVED.md",
        "regression/tools/check_521001_13_v424.py",
        "skills/lispcad/router/RULE_COVERAGE.yaml",
    ]
    text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in paths)
    for token in [
        "DATA_MANUFACTURING_CANONICALIZATION", "DATA_AUTO_R_CANONICALIZATION",
        "DATA_TAP_NOMINAL_VALIDATION", "THREAD_NOMINAL_REFERENCE",
        "THREAD_PREHOLE_SOURCE", "DATA_PDF_DIM_DIFF", "check_521001_13_v424.py",
    ]:
        assert token in text
    assert "every proved `M*`" in text
    assert "<=90" in text or "<=90°" in text

def test_v424_workflow_runs_regression():
    wf = (ROOT / ".github/workflows/dxf-export-tests.yml").read_text(encoding="utf-8")
    assert "check_521001_13_v424.py" in wf
