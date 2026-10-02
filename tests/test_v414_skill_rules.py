"""V4.14 documentation and approved arithmetic regression; NOT a manufacturing DXF certification."""
from pathlib import Path
import re
from decimal import Decimal as D

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE = ROOT / "skills/lispcad/versions/V4.14/SKILL_LISPCAD_V4_14_PORTABLE.md"
OLDER = ROOT / "skills/lispcad/versions/V4.13/SKILL_LISPCAD_V4_13_PORTABLE.md"
QA = ROOT / "regression/qa/520217-26_V4_14_APPROVED.md"


def test_repo_direct_release_and_preserves_v414_portable_history():
    """Repo-direct production may advance beyond the audit-only portable snapshot."""
    entrypoint = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    match = re.search(r"Current production release is [*][*](V[0-9]+[.][0-9]+)[*][*]", entrypoint)
    assert match, "Entrypoint must declare the currently approved repo-direct production release"
    active_version = match.group(1)
    major, minor = map(int, active_version[1:].split("."))
    assert (major, minor) >= (4, 14)
    router = (ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8")
    assert f"release: {active_version}" in router
    assert "runtime_default: false" in router
    assert CURRENT.is_file(), "Audit/compatibility portable snapshot must remain available"
    assert CURRENT.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.24 PORTABLE")
    historical_v414 = RELEASE.read_text(encoding="utf-8")
    assert historical_v414.startswith("# SKILL_LISPCAD V4.14 PORTABLE")
    assert "## Appendix L — V4.14" in historical_v414
    old = OLDER.read_text(encoding="utf-8")
    assert old.startswith("# SKILL_LISPCAD V4.13 PORTABLE")
    assert "## Appendix K — V4.13" in old
    assert "## Appendix L — V4.14" not in old


def test_handwritten_unfold_arithmetic_and_separate_od_sum():
    assert D("191")+D("35")+2*D("0.39")-D("0.56") == D("226.22")
    assert 2*D("69.2")+D("128.5")+D("2.4")-2*D("2.14") == D("265.02")
    assert 2*D("42.2")+D("128.5")+D("2.4")-2*D("6.02") == D("203.26")
    assert D("190")+D("9")+2*D("49.5")-4*D("7.84") == D("266.64")
    od = 2*D("16")+2*D("62.3")+D("84.6")
    assert od == D("241.20"), "five segments sum to OD, not unfolded blank"
    assert od-4*D("4.62") == D("222.72")


def test_existing_v413_strict_numeric_rule_not_duplicated_as_new():
    skill = CURRENT.read_text(encoding="utf-8")
    qa = QA.read_text(encoding="utf-8")
    assert "SOURCE_UNIT_CONFLICT" in skill
    assert "strict <0.01 mm" in skill
    assert "ALREADY APPROVED V4.13" in qa
    assert abs(D("821.153")-D("821.15")) < D("0.01")
    assert not (abs(D("821.16")-D("821.15")) < D("0.01"))


def test_all_new_semantic_rules_are_in_portable_and_modular_files():
    skill = CURRENT.read_text(encoding="utf-8")
    assert "2.4.2b V4.14" in skill
    assert "4.2.7.2 V4.14" in skill
    assert "3.1.1 V4.14" in skill
    assert "4.5.1 V4.14" in skill
    assert "Appendix L — V4.14" in skill
    reading = (ROOT/"skills/lispcad/core/DRAWING_READING.md").read_text(encoding="utf-8")
    datum = (ROOT/"skills/lispcad/core/DATUM_DIMENSION.md").read_text(encoding="utf-8")
    radius = (ROOT/"skills/lispcad/features/CHAMFER_RADIUS.md").read_text(encoding="utf-8")
    holes = (ROOT/"skills/lispcad/features/HOLES_TAPS.md").read_text(encoding="utf-8")
    validation = (ROOT/"skills/lispcad/core/VALIDATION.md").read_text(encoding="utf-8")
    assert "TWO DXFs FIRST" in reading
    assert "outer-edge dimension" in datum
    assert "semicircular notch/groove" in radius
    assert "Boolean union" in holes
    assert "PREVIOUSLY EXPORTED AI DXF" in validation
    qa = QA.read_text(encoding="utf-8")
    for code in ("010419", "010420", "010421", "010428", "010429", "010447"):
        assert code in qa
    assert "two center pairs" in qa
    assert "EXACT" in qa
