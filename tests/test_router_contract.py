from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "skills/lispcad/router/ROUTER.yaml"
COVERAGE = ROOT / "skills/lispcad/router/RULE_COVERAGE.yaml"

EXPECTED_FEATURES = {
    "HOLE",
    "TAP",
    "SLOT_STRAIGHT",
    "CURVED_SLOT",
    "KEGAKI",
    "PIASU",
    "SLIT_RELIEF",
    "RIB",
    "CHAMFER_FILLET",
    "HEMMING",
    "Z_BEND",
    "ACUTE_BEND_LT85",
    "BOXMET",
    "MATERIAL_RULES",
    "NOBI",
    "REVISION_CANCELLATION",
}


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _all_runtime_paths(router):
    paths = list(router["default_load"])
    for group_name in ("source_routes", "mode_routes", "feature_routes"):
        for route in router[group_name].values():
            paths.extend(route.get("load", []))
    return paths


def test_router_is_repo_direct_and_unknown_loads_route():
    router = _load(ROUTER)
    assert router["production_mode"] == "repo_direct"
    assert router["unknown_policy"] == "LOAD_ROUTE"
    assert router["portable_compatibility"]["runtime_default"] is False
    assert router["portable_compatibility"]["may_silently_continue_production_after_gap"] is False


def test_router_has_expected_feature_families():
    router = _load(ROUTER)
    assert EXPECTED_FEATURES <= set(router["feature_routes"])


def test_runtime_paths_exist_and_exclude_history():
    router = _load(ROUTER)
    paths = _all_runtime_paths(router)
    assert "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md" not in paths
    for rel in paths:
        assert not rel.startswith("skills/lispcad/versions/")
        assert not rel.startswith("docs/history/")
        assert (ROOT / rel).is_file(), rel


def test_dependencies_resolve():
    router = _load(ROUTER)
    feature_ids = set(router["feature_routes"])
    aliases = set(router.get("dependency_aliases", {}))
    for route in router["feature_routes"].values():
        for dep in route.get("depends_on", []):
            assert dep in feature_ids or dep in aliases, dep


def test_coverage_map_paths_exist():
    coverage = _load(COVERAGE)
    for release in coverage["release_coverage"].values():
        for key in ("active", "regression"):
            for rel in release.get(key, []):
                assert (ROOT / rel).is_file(), rel


def test_entrypoint_and_agents_use_router_not_full_portable():
    entry = (ROOT / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "skills/lispcad/router/FEATURE_CENSUS.md" in entry
    assert "skills/lispcad/router/ROUTER.yaml" in entry
    assert "skills/lispcad/router/FEATURE_CENSUS.md" in agents
    assert "skills/lispcad/router/ROUTER.yaml" in agents
    assert "Read the resolved portable skill **in full**" not in agents


def test_portable_snapshot_remains_available_for_audit_only():
    router = _load(ROUTER)
    rel = router["portable_compatibility"]["path"]
    assert (ROOT / rel).is_file()
    assert router["portable_compatibility"]["runtime_default"] is False
