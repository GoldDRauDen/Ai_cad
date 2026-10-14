"""V4.25 DATA-first / manufacturing-second source-preservation hardening."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
V424 = ROOT / "skills/lispcad/versions/V4.24/SKILL_LISPCAD_V4_24_PORTABLE.md"


def test_v425_release_wiring_and_portable_compatibility():
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8") + (ROOT / "docs/RELEASE_INDEX.md").read_text(encoding="utf-8")
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    coverage = yaml.safe_load((ROOT / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))
    assert "- **V4.25:**" in entry
    assert "V4.25" in coverage["release_coverage"]
    assert "references/DATA_RAW_TO_MANUFACTURING_CONTRACT.md" in coverage["release_coverage"]["V4.25"]["active"]
    assert CURRENT.read_bytes() == V424.read_bytes()
    assert CURRENT.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.24 PORTABLE")
    assert router["portable_compatibility"]["runtime_default"] is False


def test_v425_pdf_data_raw_contract_is_routed_and_checked():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    loads = router["source_routes"]["PDF_DATA_RAW"]["load"]
    assert "references/DATA_RAW_TO_MANUFACTURING_CONTRACT.md" in loads
    checks = router["post_route_checks"]
    for token in [
        "raw_data_snapshot_freeze",
        "same_parameter_gate_before_canonicalization",
        "manufacturing_change_ledger",
        "untouched_data_invariance",
    ]:
        assert token in checks


def test_v425_rule_tokens_and_52100120_regression():
    paths = [
        "references/DATA_RAW_TO_MANUFACTURING_CONTRACT.md",
        "references/SOURCE_DATA_CLASSIFICATION.md",
        "references/PDF_DATA_RAW_GEOMETRY_PRESERVATION.md",
        "references/DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md",
        "regression/qa/521001-20_V4_25_APPROVED.md",
        "regression/tools/check_521001_20_v425.py",
        "skills/lispcad/router/RULE_COVERAGE.yaml",
    ]
    text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in paths)
    for token in [
        "RAW_DATA_SNAPSHOT",
        "PHYSICAL_DATA_BASELINE",
        "SAME_PARAMETER_GATE",
        "MANUFACTURING_CHANGE_LEDGER",
        "UNTOUCHED_DATA_INVARIANCE_CHECK",
        "DATA_PDF_DIM_DIFF",
        "60.000709679",
        "Ø4.134",
        "Ø4.2",
        "854.75",
        "599.75",
    ]:
        assert token in text
    assert "representation" in text.lower() and "physical" in text.lower()


def test_v425_workflow_runs_regression():
    wf = (ROOT / ".github/workflows/dxf-export-tests.yml").read_text(encoding="utf-8")
    assert "check_521001_20_v425.py" in wf
