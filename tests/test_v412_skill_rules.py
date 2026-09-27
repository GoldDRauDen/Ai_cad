"""V4.12 documentation and user-approved arithmetic regression guards.

No PDF parsing or reference DXF comparison takes place in these tests; passing
them never certifies a corrected 520217-27 production DXF.
"""
from pathlib import Path
from math import isclose

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE = ROOT / "skills/lispcad/versions/V4.12/SKILL_LISPCAD_V4_12_PORTABLE.md"


def test_current_equals_immutable_v412_release():
    assert CURRENT.read_bytes() == RELEASE.read_bytes()


def test_user_approved_arithmetic():
    assert isclose(160 + 25.5 + 60.5 + 9 - 2 * 7.76, 239.48)
    assert isclose(141 + 61 + 18 - 14.62, 205.38)
    assert 12 / 2 == 6
    assert 2 * 2 == 4  # four semicircular ends on two slots


def test_material_prefix_and_sus430_exception_documented():
    skill = CURRENT.read_text(encoding="utf-8")
    rules = (ROOT / "references/MATERIAL_RULES.md").read_text(
        encoding="utf-8"
    )
    for document in (skill, rules):
        for token in ("SUS", "SP", "SS", "AL", "SUS430"):
            assert token in document
    assert "2.1.1 V4.12 Approved material-family prefix" in skill


def test_unknown_round_hole_kept_as_preview_circle():
    skill = CURRENT.read_text(encoding="utf-8")
    holes = (ROOT / "skills/lispcad/features/HOLES_TAPS.md").read_text(
        encoding="utf-8"
    )
    assert "V4.12 unresolved circular-hole Ø gate" in skill
    assert "V4.12 unresolved circular-hole diameter gate" in holes
    for doc in (skill, holes):
        assert "Magenta" in doc and "CIRCLE" in doc
        assert "POINT" in doc and "Ø?" in doc


def test_slot_radius_and_advisory_rules_in_modules():
    slots = (ROOT / "skills/lispcad/features/SLOTS.md").read_text(
        encoding="utf-8"
    )
    validation = (ROOT / "skills/lispcad/core/VALIDATION.md").read_text(
        encoding="utf-8"
    )
    assert "V4.12 count-only n-R" in slots and "R6" in slots
    assert "V4.12 shop-distance question suppression" in validation
    assert "Feature Containment" in validation
