"""Plan F3 / Phase 2: one release truth. All release pointers must agree."""
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _num(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.upper().replace("V", "").split("."))


def test_router_coverage_entry_and_skill_agree():
    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    coverage = yaml.safe_load((ROOT / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8") + (ROOT / "docs/RELEASE_INDEX.md").read_text(encoding="utf-8")
    release = router["release"]
    assert coverage["release"] == release
    m = re.search(r"Current production release is \*\*(V\d+\.\d+)\*\*", entry)
    assert m and m.group(1) == release
    newest = max(coverage["release_coverage"], key=lambda k: _num(k) if k.startswith("V") else (0,))
    assert newest == release, f"release_coverage newest {newest} != router {release}"


def test_schema_pointer_is_current():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "CANONICAL_INPUT_SCHEMA_V434.md" in skill
    assert "at the present repo revision" not in skill


def test_default_contract_is_v434():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import canonical_contract as cc
    assert cc.CONTRACT == "TrainAiCad-CANONICAL-V4.34"
    assert cc.CONTRACT_V431 in cc.SUPPORTED_CONTRACTS


def test_v431_job_without_legacy_flag_is_rejected():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import canonical_contract as cc
    job = {"canonical_contract": cc.CONTRACT_V431, "job_id": "X", "parts": [{"code": "A"}]}
    try:
        cc.validate_canonical_job(job)
    except cc.CanonicalContractError as exc:
        assert "legacy-only" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("V4.31 without legacy_fixture must be rejected")
