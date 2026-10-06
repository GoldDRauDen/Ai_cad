"""V4.31 E2E source-member -> canonical -> saved-DXF completeness hardening."""
from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _release_number(value: str) -> int:
    return int(str(value).upper().replace("V4.", ""))


def test_v431_release_wiring():
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    coverage = yaml.safe_load((ROOT / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))
    assert "Current production release is **V4.31**" in entry
    assert "- **V4.31:**" in entry
    assert _release_number(router["release"]) >= 31
    assert _release_number(coverage["release"]) >= 31
    assert "V4.31" in coverage["release_coverage"]


def test_v431_router_loads_executable_contract_before_census():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    loads = router["default_load"]
    ref = "references/CANONICAL_MEMBER_COMPLETENESS.md"
    census = "skills/lispcad/router/FEATURE_CENSUS.md"
    assert ref in loads and loads.index(ref) < loads.index(census)
    for gate in [
        "source_group_member_ledger",
        "proved_source_to_canonical_member_equality",
        "canonical_to_saved_dxf_entity_id_equality",
        "saved_dxf_readback",
    ]:
        assert gate in router["post_route_checks"]


def test_v431_contract_and_serializer_tokens():
    paths = [
        "references/CANONICAL_MEMBER_COMPLETENESS.md",
        "tools/CANONICAL_INPUT_SCHEMA_V431.md",
        "tools/canonical_contract.py",
        "tools/export_canonical_dxf.py",
        "regression/qa/521005-05_V4_31_APPROVED.md",
        "regression/tools/check_521005_05_v431.py",
    ]
    text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in paths)
    for token in [
        "NO_DIRECT_DXF_FROM_INTERPRETATION",
        "SOURCE_FEATURE_COMPLETENESS_FAIL",
        "PROVED_SOURCE_MEMBERS_EQ_CANONICAL",
        "CANONICAL_ENTITY_IDS_EQ_SAVED_DXF_ENTITY_IDS",
        "TrainAiCad-CANONICAL-V4.31",
        "TRAINAICAD",
        "057862", "057864", "057873",
        "REGRESSION_COVERAGE_GAP",
    ]:
        assert token in text


def test_v431_normal_entrypoint_names_canonical_serializer():
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    assert "tools/export_canonical_dxf.py" in entry
    assert "NO_DIRECT_DXF_FROM_INTERPRETATION" in entry
    assert "PROVED SOURCE MEMBERS" in entry
    assert "SAVED DXF ENTITY IDs" in entry


def test_v431_regression_executes_real_serializer_and_readback():
    runner = ROOT / "regression/tools/check_521005_05_v431.py"
    cp = subprocess.run([sys.executable, str(runner)], cwd=ROOT, text=True, capture_output=True, check=True)
    assert cp.stdout.startswith("PASS:")


def test_v431_workflow_runs_regression():
    wf = (ROOT / ".github/workflows/dxf-export-tests.yml").read_text(encoding="utf-8")
    assert "V4.19-V4.31" in wf
    assert "check_521005_05_v431.py" in wf
