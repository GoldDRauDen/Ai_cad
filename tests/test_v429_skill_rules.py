"V4.29 source-manufacturing-note / custom slit guardrails."
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _release_number(value: str) -> int:
    return int(str(value).upper().replace("V4.", ""))


def test_v429_release_wiring():
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    coverage = yaml.safe_load((ROOT / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))
    assert "- **V4.29:**" in entry
    assert _release_number(router["release"]) >= 29
    assert _release_number(coverage["release"]) >= 29
    assert "V4.29" in coverage["release_coverage"]


def test_v429_source_note_gate_precedes_feature_census():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    note_ref = "references/SOURCE_MANUFACTURING_NOTE_CENSUS.md"
    census = "skills/lispcad/router/FEATURE_CENSUS.md"
    assert note_ref in router["default_load"]
    assert router["default_load"].index(note_ref) < router["default_load"].index(census)
    assert "source_manufacturing_note_census" in router["post_route_checks"]
    assert router["feature_routes"]["SLIT_RELIEF"]["load"] == ["skills/lispcad/features/SLIT_RELIEF.md"]


def test_v429_custom_slit_is_instruction_driven_not_hardcoded():
    paths = [
        "references/SOURCE_MANUFACTURING_NOTE_CENSUS.md",
        "skills/lispcad/router/FEATURE_CENSUS.md",
        "skills/lispcad/features/SLIT_RELIEF.md",
        "skills/lispcad/core/CROSS_FEATURE_VALIDATION.md",
        "regression/qa/521005-13_V4_29_APPROVED.md",
        "regression/tools/check_521005_13_v429.py",
    ]
    text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in paths)
    for token in [
        "SOURCE_MANUFACTURING_NOTE_CENSUS",
        "SOURCE_NOTE_TO_FAMILY",
        "SOURCE_NOTE_FEATURE_COMPLETENESS",
        "CUSTOM_SOURCE_SLIT",
        "custom source-instructed slit",
        "Instruction required",
        "Never hardcode",
        "not a universal",
        "スリット 8",
        "058155",
        "058156",
    ]:
        assert token in text


def test_v429_regression_asset_and_workflow():
    assert (ROOT / "regression/assets/521005-13/SLIT_FIXTURE.dxf").is_file()
    wf = (ROOT / ".github/workflows/dxf-export-tests.yml").read_text(encoding="utf-8")
    assert "V4.19-V4.30" in wf
    assert "check_521005_13_v429.py" in wf
