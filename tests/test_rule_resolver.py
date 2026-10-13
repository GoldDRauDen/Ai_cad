"""Fail-closed deterministic routing and authority regression tests."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("resolve_rules", ROOT / "tools/resolve_rules.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
ROUTER = yaml.safe_load((ROOT / mod.ROUTER).read_text(encoding="utf-8"))


def census(source="PDF_ONLY", mode="FLAT_NO_BEND"):
    return {
        "source_mode": source,
        "part_mode": mode,
        "features": {key: {"state": "NO"} for key in ROUTER["feature_routes"]},
    }


def test_minimal_flat_route_does_not_load_history_or_regressions():
    result = mod.resolve_rules(census())
    paths = result["rule_paths"]
    assert paths.count("skills/lispcad/core/VALIDATION.md") == 1
    assert "skills/lispcad/modes/FLAT_NO_BEND.md" in paths
    assert not any(p.startswith(mod.FORBIDDEN) for p in paths)
    assert result["release"] == ROUTER["release"]


def test_tap_dependencies_and_unknown_bend_are_not_dropped():
    x = census("PDF_DATA_RAW", "UNKNOWN")
    x["features"]["TAP"]["state"] = "YES"
    x["features"]["NOBI"]["state"] = "UNKNOWN"
    output = mod.resolve_rules(x)
    paths = output["rule_paths"]
    assert "references/THREAD_PILOT_TABLE.md" in paths
    assert "references/DATA_PHYSICAL_CENSUS_AND_BIDIRECTIONAL_QA.md" in paths
    assert "skills/lispcad/modes/BEND_UNFOLD.md" in paths
    assert "HOLE" in output["loaded_feature_routes"]
    assert paths.count("skills/lispcad/features/HOLES_TAPS.md") == 1


def test_revision_route_is_a_rule_not_specific_regression_geometry():
    x = census()
    x["features"]["REVISION_CANCELLATION"]["state"] = "YES"
    paths = mod.resolve_rules(x)["rule_paths"]
    assert "skills/lispcad/features/REVISION_CANCELLATION.md" in paths
    assert "regression/datum/520709-07_APPROVED.md" not in paths


def test_incomplete_census_is_not_silently_interpreted_as_no():
    x = census()
    del x["features"]["TAP"]
    with pytest.raises(mod.ResolutionError, match="missing"):
        mod.resolve_rules(x)


def test_unknown_feature_always_loads_route():
    x = census()
    x["features"]["CURVED_SLOT"]["state"] = "UNKNOWN"
    assert "skills/lispcad/features/CURVED_SLOT.md" in mod.resolve_rules(x)["rule_paths"]


def test_no_runtime_route_can_select_historical_or_regression_file():
    router = deepcopy(ROUTER)
    router["feature_routes"]["HOLE"]["load"] = ["regression/datum/520709-07_APPROVED.md"]
    x = census()
    x["features"]["HOLE"]["state"] = "YES"
    with pytest.raises(mod.ResolutionError, match="Forbidden"):
        mod.resolve_rules(x, router=router)


def test_catalog_cannot_claim_portable_as_production_authority():
    catalog = yaml.safe_load((ROOT / "regression/error_catalog/ERROR_INDEX.yaml").read_text(encoding="utf-8"))
    assert catalog["active_production_skill"] == "AI_ENTRYPOINT.md"
    assert "repo-direct" in catalog["authority"]["priority"][1]
