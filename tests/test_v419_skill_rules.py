"""V4.19 520929-25 production-skill regression."""
from pathlib import Path
import subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/"skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE=ROOT/"skills/lispcad/versions/V4.19/SKILL_LISPCAD_V4_19_PORTABLE.md"
OLD=ROOT/"skills/lispcad/versions/V4.18/SKILL_LISPCAD_V4_18_PORTABLE.md"
QA=ROOT/"regression/qa/520929-25_V4_19_APPROVED.md"
RUNNER=ROOT/"regression/tools/check_520929_25_v419.py"
PROTOCOL=ROOT/"references/FACE_GRAPH_UNFOLD_PROTOCOL.md"

def test_release_and_routing():
    entry=(ROOT/"AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    skill=CURRENT.read_text(encoding="utf-8")
    assert "Current production release is **V4.19**" in entry
    assert CURRENT.read_bytes()==RELEASE.read_bytes()
    assert skill.startswith("# SKILL_LISPCAD V4.19 PORTABLE")
    assert OLD.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.18 PORTABLE")
    assert "520929-25_V4_19_APPROVED.md" in entry
    assert "check_520929_25_v419.py" in entry
    assert "FACE_GRAPH_UNFOLD_PROTOCOL.md" in entry

def test_v419_hard_gates_present():
    skill=CURRENT.read_text(encoding="utf-8")
    protocol=PROTOCOL.read_text(encoding="utf-8")
    for token in [
        "TOPOLOGY_LOCKED","DIMENSION_WITNESS_LOCKED","FEATURE_OWNERSHIP_LOCKED",
        "FACE_ORDER_LOCKED","BEND_SIGN_LOCKED","BEND_DOMAIN_LOCKED",
        "CONSTRAINTS_CLOSED","FOLD_BACK_MATCH","DXF_READBACK_MATCH"
    ]:
        assert token in skill
        assert token in protocol

def test_approved_regression_record():
    qa=QA.read_text(encoding="utf-8")
    assert "145.6 / 150.0" in qa
    assert "102.2/106.0" in qa
    assert "159.36/163.98" in qa
    assert "opposite fold signs" in qa

def test_executable():
    cp=subprocess.run([sys.executable,str(RUNNER)],cwd=ROOT,text=True,capture_output=True,check=True)
    assert cp.stdout.startswith("PASS:")
