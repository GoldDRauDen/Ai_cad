#!/usr/bin/env python3
"""Deterministically resolve the approved TrainAiCad rule set from a complete census.

Does not interpret source drawings, evaluate engineering evidence, or run CAD/QA.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
ROUTER = "skills/lispcad/router/ROUTER.yaml"
BOOTSTRAP = (
    "AI_BOOTSTRAP.md",
    "AI_ENTRYPOINT.md",
    "skills/lispcad/router/FEATURE_CENSUS.md",
    ROUTER,
    "skills/lispcad/router/RULE_COVERAGE.yaml",
)
FORBIDDEN = (
    "skills/lispcad/versions/",
    "skills/lispcad/portable/",
    "docs/history/",
    "regression/",
)
STATES = {"YES", "NO", "UNKNOWN"}


class ResolutionError(ValueError):
    """Incomplete census, missing dependency or unsafe routing contract."""


def _state(value: object, family: str) -> str:
    state = value.get("state") if isinstance(value, dict) else value
    if state not in STATES:
        raise ResolutionError(f"{family}: state must be YES, NO or UNKNOWN")
    return state


def resolve_rules(census: dict, root: Path = ROOT, router: dict | None = None) -> dict:
    """Return ordered, de-duplicated paths. Unknown features load their routes."""
    root = Path(root).resolve()
    if router is None:
        router = yaml.safe_load((root / ROUTER).read_text(encoding="utf-8"))
    if not isinstance(census, dict) or not isinstance(router, dict):
        raise ResolutionError("Census and Router must be mappings")
    if router.get("production_mode") != "repo_direct" or router.get("unknown_policy") != "LOAD_ROUTE":
        raise ResolutionError("Unsupported Router authority or UNKNOWN handling")

    source_mode = census.get("source_mode")
    part_mode = census.get("part_mode")
    if source_mode not in router["source_routes"]:
        raise ResolutionError(f"Unknown source_mode: {source_mode!r}")
    if part_mode not in router["mode_routes"]:
        raise ResolutionError(f"Unknown part_mode: {part_mode!r}")
    features = census.get("features")
    if not isinstance(features, dict):
        raise ResolutionError("Complete features mapping required")
    required = set(router["feature_routes"])
    supplied = set(features)
    if required != supplied:
        raise ResolutionError(
            f"Feature census mismatch: missing={sorted(required - supplied)}, "
            f"extra={sorted(supplied - required)}"
        )

    result: list[str] = []
    seen_paths: set[str] = set()

    def add_path(path: str) -> None:
        if not isinstance(path, str) or not path or "\\" in path:
            raise ResolutionError(f"Invalid route path: {path!r}")
        if path.startswith(FORBIDDEN) or path.startswith("/") or ".." in Path(path).parts:
            raise ResolutionError(f"Forbidden production route: {path}")
        resolved = (root / path).resolve()
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise ResolutionError(f"Missing or unsafe route file: {path}")
        if path not in seen_paths:
            seen_paths.add(path)
            result.append(path)

    def add_group(group: str, name: str) -> None:
        routes = router.get(group, {})
        if name not in routes:
            raise ResolutionError(f"Unknown route: {group}.{name}")
        for path in routes[name].get("load", []):
            add_path(path)

    for path in BOOTSTRAP:
        add_path(path)
    for path in router.get("default_load", []):
        add_path(path)
    add_group("source_routes", source_mode)
    add_group("mode_routes", part_mode)

    visited: set[str] = set()
    aliases = router.get("dependency_aliases", {})

    def visit(feature: str, chain: tuple[str, ...] = ()) -> None:
        if feature in chain:
            raise ResolutionError("Route dependency cycle: " + " -> ".join((*chain, feature)))
        if feature in aliases:
            alias = aliases[feature]
            add_group(alias["route_group"], alias["route_id"])
            return
        if feature in visited:
            return
        route = router["feature_routes"].get(feature)
        if route is None:
            raise ResolutionError(f"Unresolved dependency: {feature}")
        for dependency in route.get("depends_on", []):
            visit(dependency, (*chain, feature))
        visited.add(feature)
        add_group("feature_routes", feature)

    selected = []
    for name in router["feature_routes"]:
        if _state(features[name], name) != "NO":
            selected.append(name)
            visit(name)

    return {
        "release": router["release"],
        "production_mode": "repo_direct",
        "source_mode": source_mode,
        "part_mode": part_mode,
        "selected_features": selected,
        "loaded_feature_routes": sorted(visited),
        "rule_paths": result,
        "post_route_checks": list(router["post_route_checks"]),
        "note": "Route resolution only; source inspection, geometry, QA and export are separate.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("census", type=Path, help="Complete Feature Census JSON")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        census = json.loads(args.census.read_text(encoding="utf-8"))
        result = resolve_rules(census, args.repo_root)
    except (ValueError, OSError, KeyError, yaml.YAMLError) as exc:
        print(f"ROUTING_COVERAGE_GAP: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
