"""V4.16 production-skill regression."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/"skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE=ROOT/"skills/lispcad/versions/V4.16/SKILL_LISPCAD_V4_16_PORTABLE.md"
OLD=ROOT/"skills/lispcad/versions/V4.15/SKILL_LISPCAD_V4_15_PORTABLE.md"
def test_v416_preserved_and_routing_retained():
    entry=(ROOT/"AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    skill=CURRENT.read_text(encoding="utf-8")
    assert RELEASE.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.16 PORTABLE")
    assert OLD.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.15 PORTABLE")
    assert "Face-first dimension ownership" in skill
    assert "Explicit R/C family quantity closure" in skill
    assert "BOXMET-style four-flange box slit relief" in skill
    assert "BOXMET_SLIT_RELIEF.md" in entry
def test_modules():
    assert "V4.16 Face-First Dimension Ownership" in (ROOT/"skills/lispcad/core/DATUM_DIMENSION.md").read_text(encoding="utf-8")
    assert "V4.16 Explicit R/C family quantity closure" in (ROOT/"skills/lispcad/features/CHAMFER_RADIUS.md").read_text(encoding="utf-8")
    assert "V4.16 BOXMET-style four-flange box routing" in (ROOT/"skills/lispcad/modes/BEND_UNFOLD.md").read_text(encoding="utf-8")
    assert "Trigger / no-trigger gate" in (ROOT/"references/BOXMET_SLIT_RELIEF.md").read_text(encoding="utf-8")
def test_executable():
    cp=subprocess.run([sys.executable,str(ROOT/"regression/tools/check_520801_04_v416.py")],cwd=ROOT,text=True,capture_output=True,check=True)
    assert cp.stdout.startswith("PASS:")
