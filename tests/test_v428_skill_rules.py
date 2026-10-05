"""V4.28 face-creation / local bend-domain guardrails."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_v428_release_wiring():
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    coverage = yaml.safe_load((ROOT / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))
    assert "Current production release is **V4.28**" in entry
    assert "- **V4.28:**" in entry
    assert router["release"] == "V4.28"
    assert coverage["release"] == "V4.28"
    assert "V4.28" in coverage["release_coverage"]


def test_v428_mode_routes_load_face_creation_guard():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    ref = "references/FACE_CREATION_BEND_EVIDENCE.md"
    for mode in ["BEND", "MULTI_FACE", "UNKNOWN"]:
        assert ref in router["mode_routes"][mode]["load"]


def test_v428_rule_tokens_and_regression_assets():
    paths = [
        "references/FACE_CREATION_BEND_EVIDENCE.md",
        "regression/qa/521005-02_V4_28_APPROVED.md",
        "regression/tools/check_521005_02_v428.py",
    ]
    text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in paths)
    for token in [
        "FACE_CREATION_REQUIRES_BEND_EVIDENCE",
        "SAME_FACE_FIRST",
        "LOCAL_BEND_DOMAIN_BEFORE_UNFOLD",
        "THEORETICAL_SHARP_CLOSURE_FOR_R_CONTOURS",
        "AI_TOPOLOGY_ERROR",
        "057869",
        "057871",
    ]:
        assert token in text


def test_v428_workflow_runs_regression():
    wf = (ROOT / ".github/workflows/dxf-export-tests.yml").read_text(encoding="utf-8")
    assert "V4.19-V4.28" in wf
    assert "check_521005_02_v428.py" in wf
