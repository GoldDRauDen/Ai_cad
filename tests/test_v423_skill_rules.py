"""V4.23 physical DATA census, bidirectional QA and per-bend witness hard gates."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/"skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE=ROOT/"skills/lispcad/versions/V4.23/SKILL_LISPCAD_V4_23_PORTABLE.md"
PREV=ROOT/"skills/lispcad/versions/V4.22/SKILL_LISPCAD_V4_22_PORTABLE.md"

def test_v423_historical_release_and_v424_inheritance():
    entry=(ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8") + (ROOT / "docs/RELEASE_INDEX.md").read_text(encoding="utf-8")
    skill=CURRENT.read_text(encoding="utf-8")
    assert "- **V4.23:**" in entry
    assert RELEASE.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.23 PORTABLE")
    assert skill.startswith("# SKILL_LISPCAD V4.24 PORTABLE")
    assert "V4.23 direct approval / PUSH" in skill
    assert "V4.24 direct approval" not in RELEASE.read_text(encoding="utf-8")
    assert PREV.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.22 PORTABLE")
    assert "V4.23 direct approval" not in PREV.read_text(encoding="utf-8")

def test_v423_physical_census_bidirectional_and_bend_wiring():
    entry=(ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8") + (ROOT / "docs/RELEASE_INDEX.md").read_text(encoding="utf-8")
    physical=(ROOT/"references/DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md").read_text(encoding="utf-8")
    graph=(ROOT/"references/FACE_GRAPH_UNFOLD_PROTOCOL.md").read_text(encoding="utf-8")
    validation=(ROOT/"skills/lispcad/core/VALIDATION.md").read_text(encoding="utf-8")
    qa=(ROOT/"regression/qa/521001-03_V4_23_APPROVED.md").read_text(encoding="utf-8")
    checker=(ROOT/"regression/tools/check_521001_03_v423.py").read_text(encoding="utf-8")
    for token in [
        "SOURCE_PHYSICAL_TO_CANONICAL",
        "CANONICAL_TO_SOURCE_PHYSICAL",
        "PER_BEND_WITNESS_LEDGER",
        "THICKNESS_SINGLE_USE",
        "THICKNESS_REPRESENTATION",
        "check_521001_03_v423.py",
    ]:
        assert token in (entry+"\n"+physical+"\n"+graph+"\n"+validation+"\n"+qa+"\n"+checker)
    assert "REFERENCE_ANOMALY" in qa
    assert "057417" in qa and "057294" in qa
