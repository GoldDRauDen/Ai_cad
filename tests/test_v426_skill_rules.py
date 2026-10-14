"""V4.26 DXF source physical-curve decoding hardening."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
V424 = ROOT / "skills/lispcad/versions/V4.24/SKILL_LISPCAD_V4_24_PORTABLE.md"


def test_v426_release_wiring_and_portable_compatibility():
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8") + (ROOT / "docs/RELEASE_INDEX.md").read_text(encoding="utf-8")
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    coverage = yaml.safe_load((ROOT / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))
    assert "- **V4.26:**" in entry
    assert "V4.26" in coverage["release_coverage"]
    assert "references/DXF_PHYSICAL_CURVE_DECODING.md" in coverage["release_coverage"]["V4.26"]["active"]
    assert CURRENT.read_bytes() == V424.read_bytes()
    assert CURRENT.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.24 PORTABLE")
    assert router["portable_compatibility"]["runtime_default"] is False


def test_v426_decoder_is_always_loaded_before_feature_census():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    loads = router["default_load"]
    decoder = "references/DXF_PHYSICAL_CURVE_DECODING.md"
    census = "skills/lispcad/router/FEATURE_CENSUS.md"
    assert decoder in loads
    assert loads.index(decoder) < loads.index(census)
    assert "physical_curve_decode_before_feature_census" in router["post_route_checks"]


def test_v426_bulge_hard_gate_tokens_and_regression_wiring():
    paths = [
        "references/DXF_PHYSICAL_CURVE_DECODING.md",
        "skills/lispcad/router/FEATURE_CENSUS.md",
        "regression/qa/521001-19_V4_26_APPROVED.md",
        "regression/tools/check_521001_19_v426.py",
        "skills/lispcad/router/RULE_COVERAGE.yaml",
    ]
    text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in paths)
    for token in [
        "DXF_PHYSICAL_CURVE_DECODE_BEFORE_CENSUS",
        "POLYLINE_BULGE_IS_ARC",
        "PHYSICAL_CURVE_CENSUS",
        "BULGE_ARC_NOT_CHORD",
        "theta = 4 * atan(b)",
        "final-vertex -> first-vertex",
        "057688/113",
        "057689/114",
        "2-R3",
        "2-R1",
    ]:
        assert token in text


def test_v426_workflow_runs_regression():
    wf = (ROOT / ".github/workflows/dxf-export-tests.yml").read_text(encoding="utf-8")
    assert "check_521001_19_v426.py" in wf
