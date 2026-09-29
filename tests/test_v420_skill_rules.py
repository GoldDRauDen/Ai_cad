"""V4.20 source/data classification + mechanical feature hardening."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/"skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE=ROOT/"skills/lispcad/versions/V4.20/SKILL_LISPCAD_V4_20_PORTABLE.md"
OLD=ROOT/"skills/lispcad/versions/V4.19/SKILL_LISPCAD_V4_19_PORTABLE.md"
RUNNER=ROOT/"regression/tools/check_v420_source_mech.py"

def test_release_and_routing():
    entry=(ROOT/"AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    skill=CURRENT.read_text(encoding="utf-8")
    assert "Current production release is **V4.20**" in entry
    assert CURRENT.read_bytes()==RELEASE.read_bytes()
    assert skill.startswith("# SKILL_LISPCAD V4.20 PORTABLE")
    assert OLD.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.19 PORTABLE")
    for token in ["SOURCE_DATA_CLASSIFICATION.md","MECHANICAL_CLASSIFIER.md","520928-20_V4_20_APPROVED.md","HD4_V4_20_APPROVED.md","SILT_GT90_V4_20_APPROVED.md"]:
        assert token in entry

def test_source_threshold_and_modes():
    s=(ROOT/"references/SOURCE_DATA_CLASSIFICATION.md").read_text(encoding="utf-8")
    for token in ["PDF_ONLY","PDF_DATA_RAW","TRAIN_REFERENCE","DIRECT_EXISTING_DXF_AUDIT"]:
        assert token in s
    assert "Delta < 0.1 mm" in s and "Delta >= 0.1 mm" in s
    assert "Delta < 1.0 mm" in s and "Delta >= 1.0 mm" in s

def test_mechanical_modules():
    for p in ["references/MECHANICAL_CLASSIFIER.md","skills/lispcad/features/KEGAKI.md","skills/lispcad/features/SLIT_RELIEF.md","skills/lispcad/features/RIB.md","skills/lispcad/features/CURVED_SLOT.md"]:
        assert (ROOT/p).exists()
    assert "D = t * sin(theta)" in (ROOT/"skills/lispcad/features/SLIT_RELIEF.md").read_text(encoding="utf-8")
    assert "exactly ONE closed internal CUT contour" in (ROOT/"skills/lispcad/features/CURVED_SLOT.md").read_text(encoding="utf-8")

def test_executable():
    cp=subprocess.run([sys.executable,str(RUNNER)],cwd=ROOT,text=True,capture_output=True,check=True)
    assert cp.stdout.startswith("PASS:")
