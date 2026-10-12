"""Fail-closed rule coverage, staged loading, and topology/forming protection."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_rule_coverage import CoverageError, audit  # noqa: E402
from resolve_rules import ResolutionError, resolve_rules  # noqa: E402

ROUTER = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text())


def census(source="PDF_ONLY", mode="FLAT_NO_BEND", reference="NO"):
    return {
        "source_mode": source,
        "part_mode": mode,
        "reference_present": reference,
        "features": {key: {"state": "NO"} for key in ROUTER["feature_routes"]},
    }


def test_every_active_module_is_router_reachable():
    report = audit()
    assert report["status"] == "PASS"
    assert report["active_module_count"] >= 44
    assert report["routed_active_module_count"] == report["active_module_count"]
    assert report["unreachable_active_modules"] == []


@pytest.mark.parametrize("feature,path", [
    ("STEPPED_NOTCHED", "skills/lispcad/topology/STEPPED_PROFILE.md"),
    ("L_PROFILE", "skills/lispcad/topology/L_PROFILE.md"),
    ("U_PROFILE", "skills/lispcad/topology/U_PROFILE.md"),
    ("MULTI_FACE_PROFILE", "skills/lispcad/topology/MULTI_FACE_PROFILE.md"),
    ("FORMING_FEATURES", "skills/lispcad/features/FORMING_FEATURES.md"),
])
def test_missing_previous_topology_or_forming_route_is_included(feature, path):
    x = census()
    x["features"][feature]["state"] = "YES"
    r = resolve_rules(x)
    assert path in r["stage_plans"]["L2_GEOMETRY"]["rule_paths"]


def test_unrouted_active_stepped_flange_fails_gate():
    x = deepcopy(ROUTER)
    x["feature_routes"]["STEPPED_NOTCHED"]["load"] = []
    with pytest.raises(CoverageError, match="UNREACHABLE_ACTIVE_RULE"):
        audit(router=x)


def test_legacy_missing_feature_is_fail_closed_not_no():
    x = census()
    del x["features"]["STEPPED_NOTCHED"]
    with pytest.raises(ResolutionError, match="STEPPED_NOTCHED"):
        resolve_rules(x)


def test_staged_deferred_validation_is_mandatory_but_not_preloaded():
    x = census()
    r = resolve_rules(x)
    stages = r["stage_plans"]
    assert r["stage_order"] == [
        "L0_BOOTSTRAP", "L1_SOURCE_CENSUS",
        "L2_GEOMETRY", "L3_VALIDATE_EXPORT_QA",
    ]
    assert "skills/lispcad/core/VALIDATION.md" not in stages["L0_BOOTSTRAP"]["rule_paths"]
    assert "skills/lispcad/core/VALIDATION.md" not in stages["L1_SOURCE_CENSUS"]["rule_paths"]
    assert "skills/lispcad/core/VALIDATION.md" in stages["L3_VALIDATE_EXPORT_QA"]["rule_paths"]
    assert "references/HOLISTIC_ENGINEERING_CHALLENGE.md" in stages["L3_VALIDATE_EXPORT_QA"]["rule_paths"]
    assert "references/CANONICAL_MEMBER_COMPLETENESS.md" in stages["L1_SOURCE_CENSUS"]["rule_paths"]
    assert "proved_source_to_canonical_member_equality" in r["post_route_checks"]
    assert len(r["rule_paths"]) == len(set(r["rule_paths"]))
    assert r["new_bytes_total"] == sum(
        stages[s]["new_bytes"] for s in r["stage_order"]
    )


def test_source_mode_drives_data_curve_decoder():
    p = "references/DXF_PHYSICAL_CURVE_DECODING.md"
    x = census(source="PDF_ONLY")
    assert p in resolve_rules(x)["stage_plans"]["L1_SOURCE_CENSUS"]["rule_paths"]
    for mode in ("PDF_DATA_RAW", "TRAIN_REFERENCE", "DIRECT_EXISTING_DXF_AUDIT"):
        x = census(source=mode)
        assert p in resolve_rules(x)["stage_plans"]["L1_SOURCE_CENSUS"]["rule_paths"]


def test_reference_firewall_not_skipped_when_unknown():
    p = "references/REFERENCE_EXPOSURE_FIREWALL.md"
    assert p not in resolve_rules(census(reference="NO"))["rule_paths"]
    for state in ("YES", "UNKNOWN"):
        assert p in resolve_rules(census(reference=state))["rule_paths"]


def test_unknown_topology_loads_rule_instead_of_assuming_no():
    x = census()
    x["features"]["STEPPED_NOTCHED"]["state"] = "UNKNOWN"
    assert "skills/lispcad/topology/STEPPED_PROFILE.md" in resolve_rules(x)["rule_paths"]


def test_unexpected_stage_map_fails_closed():
    x = deepcopy(ROUTER)
    del x["stage_routes"]["L3_VALIDATE_EXPORT_QA"]
    with pytest.raises(ResolutionError, match="mandatory stage_routes"):
        resolve_rules(census(), router=x)


def test_forbidden_regression_path_in_deferred_stage_cannot_execute():
    x = deepcopy(ROUTER)
    x["stage_routes"]["L3_VALIDATE_EXPORT_QA"]["load"] = [
        "regression/datum/520709-07_APPROVED.md"
    ]
    with pytest.raises(ResolutionError, match="Forbidden"):
        resolve_rules(census(), router=x)
