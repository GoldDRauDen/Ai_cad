"""V4.30 source-feature-group, reference-parameter and 90-degree bend-end relief hardening."""
from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _release_number(value: str) -> int:
    return int(str(value).upper().replace("V4.", ""))


def test_v430_release_wiring():
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    coverage = yaml.safe_load((ROOT / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))
    assert "Current production release is **V4.30**" in entry
    assert "- **V4.30:**" in entry
    assert _release_number(router["release"]) >= 30
    assert _release_number(coverage["release"]) >= 30
    assert "V4.30" in coverage["release_coverage"]


def test_v430_default_gates_precede_feature_census():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    loads = router["default_load"]
    guard = "references/RUNTIME_AUTHORITY_GUARD.md"
    groups = "references/SOURCE_FEATURE_GROUP_CLOSURE.md"
    census = "skills/lispcad/router/FEATURE_CENSUS.md"
    assert guard in loads
    assert groups in loads
    assert loads.index(guard) < loads.index(census)
    assert loads.index(groups) < loads.index(census)
    assert "source_feature_group_closure" in router["post_route_checks"]
    assert "same_physical_parameter_before_reference_conflict" in router["post_route_checks"]


def test_v430_bend_modes_load_bend_edge_relief_gate():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    ref = "references/BEND_EDGE_RELIEF_90.md"
    for mode in ["BEND", "MULTI_FACE", "UNKNOWN"]:
        assert ref in router["mode_routes"][mode]["load"]
    assert "bend_edge_length_lock" in router["post_route_checks"]
    assert "bend_end_offset_relief_90" in router["post_route_checks"]


def test_v430_rule_tokens_and_boundaries():
    paths = [
        "references/RUNTIME_AUTHORITY_GUARD.md",
        "references/SOURCE_FEATURE_GROUP_CLOSURE.md",
        "references/BEND_EDGE_RELIEF_90.md",
        "regression/qa/521005-05_V4_30_APPROVED.md",
        "regression/tools/check_521005_05_v430.py",
    ]
    text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in paths)
    for token in [
        "RUNTIME_AUTHORITY_GUARD",
        "LEGACY_COMPATIBILITY_TEXT",
        "SOURCE_FEATURE_GROUP",
        "GROUP_COUNT_CLOSURE",
        "SAME_PHYSICAL_PARAMETER_BEFORE_REFERENCE_CONFLICT",
        "CUSTOMER_CONFIRMATION_PENDING",
        "BEND_EDGE_LENGTH_LOCK",
        "BEND_END_OFFSET_90",
        "chiều dài cạnh uốn",
        "bend-edge length",
        "bend-end offset",
        "bend-relief slit",
        "|S| + T + 0.2",
        "057861",
        "057862",
        "057864",
        "057865",
        "057873",
    ]:
        assert token in text

    bend_ref = (ROOT / "references/BEND_EDGE_RELIEF_90.md").read_text(encoding="utf-8")
    assert "Case A — `S > 0`" in bend_ref
    assert "NO bend-relief slit" in bend_ref
    assert "There is no active `T/2` threshold" in bend_ref
    assert "90-degree" in bend_ref


def test_v430_regression_executes_and_reads_back_dxf():
    runner = ROOT / "regression/tools/check_521005_05_v430.py"
    cp = subprocess.run([sys.executable, str(runner)], cwd=ROOT, text=True, capture_output=True, check=True)
    assert cp.stdout.startswith("PASS:")


def test_v430_workflow_runs_regression():
    wf = (ROOT / ".github/workflows/dxf-export-tests.yml").read_text(encoding="utf-8")
    assert "V4.19-V4.30" in wf
    assert "check_521005_05_v430.py" in wf
