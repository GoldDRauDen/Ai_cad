"""V4.32 bend attachment edge ownership and formed-profile OD hardening."""
from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _release_number(value: str) -> int:
    return int(str(value).upper().replace("V4.", ""))


def test_v432_release_wiring():
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    coverage = yaml.safe_load((ROOT / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))
    assert "- **V4.32:**" in entry
    assert _release_number(router["release"]) >= 32
    assert _release_number(coverage["release"]) >= 32
    assert "V4.32" in coverage["release_coverage"]


def test_v432_mode_routes_load_attachment_and_measurement_contracts():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    for mode in ["BEND", "MULTI_FACE", "UNKNOWN"]:
        loads = router["mode_routes"][mode]["load"]
        assert "references/BEND_ATTACHMENT_EDGE_OWNERSHIP.md" in loads
        assert "references/FORMED_PROFILE_OD_MEASUREMENT.md" in loads
    assert "bend_attachment_edge_lock" in router["post_route_checks"]
    assert "formed_profile_od_measurement_when_applicable" in router["post_route_checks"]


def test_v432_rule_tokens():
    paths = [
        "references/BEND_ATTACHMENT_EDGE_OWNERSHIP.md",
        "references/FORMED_PROFILE_OD_MEASUREMENT.md",
        "references/FACE_GRAPH_UNFOLD_PROTOCOL.md",
        "skills/lispcad/modes/BEND_UNFOLD.md",
        "skills/lispcad/core/DATUM_DIMENSION.md",
        "skills/lispcad/core/CROSS_FEATURE_VALIDATION.md",
        "regression/qa/521006-18_V4_32_APPROVED.md",
    ]
    text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in paths)
    for token in [
        "BEND_ATTACHMENT_EDGE_LOCKED",
        "NEAREST_VIEW_EDGE",
        "MEASUREMENT_CONSTRUCTION_VIEW",
        "physical edge identity",
        "OD_actual",
        "THICKNESS_SINGLE_USE",
        "CUSTOMER_CONFIRMATION_PENDING",
        "058648", "058653", "058655",
    ]:
        assert token in text


def test_v432_regression_executes():
    runner = ROOT / "regression/tools/check_521006_18_v432.py"
    cp = subprocess.run([sys.executable, str(runner)], cwd=ROOT, text=True, capture_output=True, check=True)
    assert cp.stdout.startswith("PASS:")


def test_v432_workflow_runs_regression():
    wf = (ROOT / ".github/workflows/dxf-export-tests.yml").read_text(encoding="utf-8")
    assert "V4.19-V4.33" in wf
    assert "check_521006_18_v432.py" in wf
