"""V4.18 520929-18 production-skill regression."""
from pathlib import Path
import subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/"skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE=ROOT/"skills/lispcad/versions/V4.18/SKILL_LISPCAD_V4_18_PORTABLE.md"
OLD=ROOT/"skills/lispcad/versions/V4.17/SKILL_LISPCAD_V4_17_PORTABLE.md"
QA=ROOT/"regression/qa/520929-18_V4_18_APPROVED.md"
RUNNER=ROOT/"regression/tools/check_520929_18_v418.py"

def test_release_and_routing():
    entry=(ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8") + (ROOT / "docs/RELEASE_INDEX.md").read_text(encoding="utf-8")
    skill=CURRENT.read_text(encoding="utf-8")
    assert RELEASE.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.18 PORTABLE")
    assert "V4.18 direct approval / PUSH" in skill
    assert OLD.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.17 PORTABLE")
    assert "520929-18_V4_18_APPROVED.md" in entry
    assert "check_520929_18_v418.py" in entry
    assert "V4.18 520929-18 hard-gate routing" in entry

def test_v418_hardening_present():
    drawing=(ROOT/"skills/lispcad/core/DRAWING_READING.md").read_text(encoding="utf-8")
    chamfer=(ROOT/"skills/lispcad/features/CHAMFER_RADIUS.md").read_text(encoding="utf-8")
    valid=(ROOT/"skills/lispcad/core/VALIDATION.md").read_text(encoding="utf-8")
    boxmet=(ROOT/"references/BOXMET_SLIT_RELIEF.md").read_text(encoding="utf-8")
    skill=CURRENT.read_text(encoding="utf-8")
    assert "V4.18 DETAILED_SOURCE_BUNDLE" in drawing
    assert "V4.18 C/R_SEMANTIC_LOCK" in chamfer
    assert "V4.18 SOURCE_CALLOUT_CANONICAL_CHECK" in valid
    assert "V4.18 BOXMET_SIGNED_ORIENTATION" in boxmet
    for token in ["DETAILED_SOURCE_BUNDLE","C/R_SEMANTIC_LOCK","SOURCE_CALLOUT_CANONICAL_CHECK","BOXMET_SIGNED_ORIENTATION"]:
        assert token in skill

def test_approved_regression_record():
    qa=QA.read_text(encoding="utf-8")
    assert "980.72" in qa and "830.72" in qa
    assert "Source PDF callout is **C2**" in qa
    assert "short ray `(0,+)`" in qa
    assert "endpoint-only contact" in qa

def test_executable():
    cp=subprocess.run([sys.executable,str(RUNNER)],cwd=ROOT,text=True,capture_output=True,check=True)
    assert cp.stdout.startswith("PASS:")
