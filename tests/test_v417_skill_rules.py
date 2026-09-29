"""V4.17 520929-10 historical hardening regression retained under later CURRENT releases."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/"skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE=ROOT/"skills/lispcad/versions/V4.17/SKILL_LISPCAD_V4_17_PORTABLE.md"
OLD=ROOT/"skills/lispcad/versions/V4.16/SKILL_LISPCAD_V4_16_PORTABLE.md"
QA=ROOT/"regression/qa/520929-10_V4_17_APPROVED.md"
RUNNER=ROOT/"regression/tools/check_520929_10_v417.py"
VALID=ROOT/"skills/lispcad/core/VALIDATION.md"

def test_release_and_routing():
    entry=(ROOT/"AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    skill=CURRENT.read_text(encoding="utf-8")
    assert "Current production release is **V4.18**" in entry
    assert RELEASE.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.17 PORTABLE")
    assert "V4.17 direct approval" in skill
    assert OLD.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.16 PORTABLE")
    assert "520929-10_V4_17_APPROVED.md" in entry

def test_hard_gates_present():
    skill=CURRENT.read_text(encoding="utf-8")
    valid=VALID.read_text(encoding="utf-8")
    qa=QA.read_text(encoding="utf-8")
    assert "V4.17 HARD MIRROR GATE" in skill
    for gate in ["SLOT_WITNESS_FAIL","MIRROR_SCOPE_FAIL","DATUM_WITNESS_FAIL","KEGAKI_SCOPE_FAIL","STALE_PREVIEW_FAIL","REFERENCE_METADATA_NONBLOCKING"]:
        assert gate in valid
    assert "width/end-diameter = 9" in qa and "R4.5" in qa
    assert "Y=32-10=22" in qa
    assert "$INSUNITS=1" in qa

def test_executable():
    cp=subprocess.run([sys.executable,str(RUNNER)],cwd=ROOT,text=True,capture_output=True,check=True)
    assert cp.stdout.startswith("PASS:")
