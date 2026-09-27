"""V4.13 user-approved 520315-18 regression and document guards.

Passing these tests cannot certify a regenerated production DXF; these
tests are arithmetic, scope and portable-document checks only.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from math import radians, tan

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE = ROOT / "skills/lispcad/versions/V4.13/SKILL_LISPCAD_V4_13_PORTABLE.md"
HISTORICAL = ROOT / "skills/lispcad/versions/V4.12/SKILL_LISPCAD_V4_12_PORTABLE.md"
QA = ROOT / "regression/qa/520315-18_V4_13_APPROVED.md"


def test_current_equals_immutable_v413_and_historical_v412_is_preserved():
    assert CURRENT.read_bytes() == RELEASE.read_bytes()
    assert CURRENT.read_text(encoding="utf-8").lstrip().startswith(
        "# SKILL_LISPCAD V4.13 PORTABLE"
    )
    old = HISTORICAL.read_text(encoding="utf-8")
    assert old.lstrip().startswith("# SKILL_LISPCAD V4.12 PORTABLE")
    assert "## Appendix J — V4.12" in old
    assert "V4.13 direct approval" not in old


def test_slot_end_center_examples_are_independent():
    w = Decimal("6.5")
    assert Decimal("4") + w == Decimal("10.5")   # 018295 C=4
    assert Decimal("10") + w == Decimal("16.5")  # 018304 C=10
    qa = QA.read_text(encoding="utf-8")
    assert "END CENTERS" in qa
    assert "OUTSIDE TIPS" in qa


def test_id_od_rounding_precedes_nobi_deduction():
    raw = Decimal(str(2 * tan(radians(7.5))))
    offset = raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    assert offset == Decimal("0.26")
    length_a = Decimal("797") + offset + Decimal("24") + offset - Decimal("0.37")
    length_b = Decimal("262") + Decimal("61.5") - Decimal("3.68")
    assert length_a == Decimal("821.15")
    assert length_b == Decimal("319.82")


def test_strict_derived_comparison_tolerance_not_source_tolerance():
    computed = Decimal("821.15")
    assert abs(Decimal("821.153") - computed) < Decimal("0.01")
    assert not (abs(Decimal("821.16") - computed) < Decimal("0.01"))
    skill = CURRENT.read_text(encoding="utf-8")
    qa = QA.read_text(encoding="utf-8")
    assert "EXACT source input" in skill
    assert "Printed 797/24/262/61.5" in qa


def test_new_nonduplicate_rules_in_portable_and_modules():
    skill = CURRENT.read_text(encoding="utf-8")
    reading = (ROOT / "skills/lispcad/core/DRAWING_READING.md").read_text(
        encoding="utf-8"
    )
    bend = (ROOT / "skills/lispcad/modes/BEND_UNFOLD.md").read_text(
        encoding="utf-8"
    )
    validation = (ROOT / "skills/lispcad/core/VALIDATION.md").read_text(
        encoding="utf-8"
    )
    for key in (
        "SOURCE_UNIT_CONFLICT",
        "INSIDE_VIEW",
        "HANDWRITTEN_NOBI_DIFFERS_FROM_TABLE",
        "strict <0.01 mm",
        "## Appendix K — V4.13",
    ):
        assert key in skill
    assert "25.4" in reading and "SOURCE_UNIT_CONFLICT" in reading
    assert "INSIDE_VIEW" in bend and "N_hand" in bend
    assert "SOURCE_UNIT_CONFLICT" in validation
    assert "V4.12 shop-distance question policy" in skill
    assert "V4.12 unresolved circular-hole Ø gate" in skill
    assert "V4.12 quantity-only" in skill
    assert "L08 explicitly deduplicated" in skill
