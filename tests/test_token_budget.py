"""Plan Phase 3: token budget guard. Budgets are regression ceilings measured after
the Phase 3 change; they stop silent growth of the per-job rule load."""
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STARTUP_BUDGET_BYTES = 138_000      # measured 136,696 after Phase 3
BEND_NEW_BYTES_BUDGET = 330_000     # measured 327,176 for BEND + HOLE/KEGAKI/MATERIAL/NOBI

FAMILIES = ("HOLE TAP SLOT_STRAIGHT CURVED_SLOT KEGAKI PIASU SLIT_RELIEF RIB FORMING_FEATURES "
            "L_PROFILE U_PROFILE MULTI_FACE_PROFILE STEPPED_NOTCHED CHAMFER_FILLET HEMMING Z_BEND "
            "ACUTE_BEND_LT85 BOXMET MATERIAL_RULES NOBI REVISION_CANCELLATION").split()


def _router():
    return yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))


def test_startup_load_within_budget():
    r = _router()
    files = ["SKILL.md", "AI_BOOTSTRAP.md", "AI_ENTRYPOINT.md",
             "skills/lispcad/router/ROUTER.yaml", "skills/lispcad/router/FEATURE_CENSUS.md"]
    files += r["default_load"]
    total = sum(os.path.getsize(ROOT / f) for f in dict.fromkeys(files))
    assert total <= STARTUP_BUDGET_BYTES, total


def test_audit_map_is_not_loaded_per_job():
    assert not any("RULE_COVERAGE" in p for p in _router()["default_load"])


def test_bend_job_rule_load_within_budget(tmp_path):
    census = {"source_mode": "PDF_DATA_RAW", "part_mode": "BEND", "reference_present": "NO",
              "customer_code": None, "source_manufacturing_notes": [],
              "features": {f: {"state": "YES" if f in ("HOLE", "KEGAKI", "MATERIAL_RULES", "NOBI")
                               else "NO", "evidence": []} for f in FAMILIES}}
    path = tmp_path / "census.json"
    path.write_text(json.dumps(census), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(ROOT / "tools/resolve_rules.py"), str(path)],
                          capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stderr
    plan = json.loads(proc.stdout)
    assert plan["release"] == "V4.34"
    assert plan["new_bytes_total"] <= BEND_NEW_BYTES_BUDGET, plan["new_bytes_total"]
