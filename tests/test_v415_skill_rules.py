"""V4.15 acute-bend <85° production-skill and reproducibility regression."""
from pathlib import Path
import re,subprocess,sys
import ezdxf
ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/"skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md"
RELEASE=ROOT/"skills/lispcad/versions/V4.15/SKILL_LISPCAD_V4_15_PORTABLE.md"
V414=ROOT/"skills/lispcad/versions/V4.14/SKILL_LISPCAD_V4_14_PORTABLE.md"
METHOD=ROOT/"references/ACUTE_BEND_LT85_METHOD.md"
FROM=ROOT/"references/ACUTE_BEND_LT85_FROM_SOURCE.md"
QA=ROOT/"regression/qa/ACUTE_BEND_LT85_APPROVED.md"
RUNNER=ROOT/"regression/tools/check_acute_bend_lt85.py"
FIX=ROOT/"regression/assets/acute_bend_lt85/ACUTE_BEND_LT85_SOURCE_FIXTURE.dxf"
PROOF=ROOT/"regression/assets/acute_bend_lt85/ACUTE_BEND_LT85_OD_PROOF.dxf"
SVG=ROOT/"regression/assets/acute_bend_lt85/ACUTE_BEND_LT85_CONSTRUCTION.svg"
BEND=ROOT/"skills/lispcad/modes/BEND_UNFOLD.md"
def test_v415_preserved_v414_preserved():
    entry=(ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8") + (ROOT / "docs/RELEASE_INDEX.md").read_text(encoding="utf-8")
    assert RELEASE.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.15 PORTABLE")
    assert V414.read_text(encoding="utf-8").startswith("# SKILL_LISPCAD V4.14 PORTABLE")
    assert "V4.15" in entry
def test_rule_routed_and_reproducible():
    skill=CURRENT.read_text(encoding="utf-8"); bend=BEND.read_text(encoding="utf-8")
    assert "4.6.2 V4.15" in skill and "ACUTE_BEND_LT85_FROM_SOURCE.md" in skill
    assert "ACUTE_BEND_LT85_FROM_SOURCE.md" in bend
    assert "theoretical sharp intersection" in METHOD.read_text(encoding="utf-8")
    assert "approved OD values" in FROM.read_text(encoding="utf-8")
    assert "job-specific regression evidence" in QA.read_text(encoding="utf-8")
def test_runner_recomputes_from_fixture():
    cp=subprocess.run([sys.executable,str(RUNNER)],cwd=ROOT,text=True,capture_output=True,check=True)
    assert "OD1: 182.014217" in cp.stdout and "OD2: 49.712236" in cp.stdout and "PASS:" in cp.stdout
def test_assets_read_back():
    f=ezdxf.readfile(FIX); p=ezdxf.readfile(PROOF)
    assert len(list(f.modelspace().query('LINE[layer=="FACE_1"]')))==4
    assert len(list(f.modelspace().query('LINE[layer=="FACE_2"]')))==4
    assert len(list(p.modelspace().query("ARC")))==2
    assert SVG.read_text(encoding="utf-8").lstrip().startswith("<svg")
