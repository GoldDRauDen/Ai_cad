"""V4.27 weld-cue / RIB-KEGAKI census guardrails."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _release_number(value: str) -> int:
    return int(str(value).upper().replace("V4.", ""))


def test_v427_release_wiring():
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    coverage = yaml.safe_load((ROOT / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))
    assert "- **V4.27:**" in entry
    assert _release_number(router["release"]) >= 27
    assert _release_number(coverage["release"]) >= 27
    assert "V4.27" in coverage["release_coverage"]


def test_v427_weld_cue_and_kegaki_guardrails():
    paths = [
        "skills/lispcad/features/KEGAKI.md",
        "skills/lispcad/router/FEATURE_CENSUS.md",
        "skills/lispcad/core/CROSS_FEATURE_VALIDATION.md",
        "regression/qa/521005-01_V4_27_APPROVED.md",
        "regression/tools/check_521005_01_v427.py",
    ]
    text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in paths)
    for token in [
        "REVERSED_E_ABOVE_BARCODE",
        "WELD_REQUIRED_CUE",
        "cannot self-locate",
        "specific KEGAKI instruction",
        "do not infer welding",
        "058061_SLOT_DATUM_APPROVED",
        "058062_058063_WELD_RIB_KEGAKI_APPROVED",
        "058064_DATUM_WITNESS_APPROVED",
    ]:
        assert token in text


def test_v427_does_not_make_rib_depend_universally_on_kegaki():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    assert "KEGAKI" not in router["feature_routes"]["RIB"].get("depends_on", [])


def test_v427_workflow_runs_regression():
    wf = (ROOT / ".github/workflows/dxf-export-tests.yml").read_text(encoding="utf-8")
    assert "check_521005_01_v427.py" in wf
