"""V4.22 source exhaustion and feature completeness hard gates."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/"skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE=ROOT/"skills/lispcad/versions/V4.22/SKILL_LISPCAD_V4_22_PORTABLE.md"
PREV=ROOT/"skills/lispcad/versions/V4.21/SKILL_LISPCAD_V4_21_PORTABLE.md"

def test_v422_historical_release_and_v424_inheritance():
    entry=(ROOT/"AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    skill=CURRENT.read_text(encoding="utf-8")
    assert "- **V4.22:**" in entry
    assert RELEASE.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.22 PORTABLE")
    assert skill.startswith("# SKILL_LISPCAD V4.24 PORTABLE")
    assert "V4.22 direct approval / PUSH" in skill
    assert PREV.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.21 PORTABLE")
    assert "V4.22 direct approval" not in PREV.read_text(encoding="utf-8")
    assert "V4.23 direct approval" not in RELEASE.read_text(encoding="utf-8")
    assert "V4.24 direct approval" not in RELEASE.read_text(encoding="utf-8")

def test_v422_source_exhaustion_and_feature_completeness_wiring():
    entry=(ROOT/"AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    graph=(ROOT/"references/FACE_GRAPH_UNFOLD_PROTOCOL.md").read_text(encoding="utf-8")
    validation=(ROOT/"skills/lispcad/core/VALIDATION.md").read_text(encoding="utf-8")
    qa=(ROOT/"regression/qa/520930-10_V4_22_APPROVED.md").read_text(encoding="utf-8")
    checker=(ROOT/"regression/tools/check_520930_10_v422.py").read_text(encoding="utf-8")
    for token in [
        "SOURCE_EXHAUSTED_BEFORE_VIEWS_ONLY",
        "SOURCE_FEATURE_COMPLETENESS",
        "check_520930_10_v422.py",
    ]:
        assert token in (entry+"\n"+graph+"\n"+validation+"\n"+qa+"\n"+checker)
    assert "PENDING_CUSTOMER_CONFIRMATION" in qa
    assert "two active slit/relief" in qa.lower()
    assert "simplified two-line/two-semicircle stadium" in qa
