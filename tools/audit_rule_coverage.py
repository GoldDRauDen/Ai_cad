#!/usr/bin/env python3
"""Fail closed when any active CAD rule module is missing from the Router.

Scope is deliberately file-level: approval/semantic correctness of individual
rules still requires engineering review and feature-specific regressions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
ROUTER = "skills/lispcad/router/ROUTER.yaml"
COVERAGE = "skills/lispcad/router/RULE_COVERAGE.yaml"
ACTIVE_GLOBS = (
    "skills/lispcad/core/*.md",
    "skills/lispcad/features/*.md",
    "skills/lispcad/modes/*.md",
    "skills/lispcad/topology/*.md",
    "references/*.md",
)
ROUTE_GROUPS = ("stage_routes", "source_routes", "mode_routes", "feature_routes")
EXCLUDED_PREFIXES = (
    "regression/", "skills/lispcad/portable/", "skills/lispcad/versions/",
    "docs/history/", "services/trainaicad-mcp/",
)


class CoverageError(ValueError):
    pass


def audit(root: Path = ROOT, router: dict | None = None) -> dict:
    root = Path(root).resolve()
    router = router if router is not None else yaml.safe_load(
        (root / ROUTER).read_text(encoding="utf-8")
    )
    coverage = yaml.safe_load((root / COVERAGE).read_text(encoding="utf-8"))
    if not isinstance(router, dict) or router.get("production_mode") != "repo_direct":
        raise CoverageError("Unsupported production Router")
    if not isinstance(coverage, dict) or coverage.get("release") != router.get("release"):
        raise CoverageError("Current Router / Coverage release mismatch")

    active = {p.relative_to(root).as_posix()
              for pattern in ACTIVE_GLOBS for p in root.glob(pattern) if p.is_file()}
    if not active:
        raise CoverageError("No production modules discovered")

    routed = set()
    required = set(router.get("default_load", []))
    routed.update(required)
    for group in ROUTE_GROUPS:
        mapping = router.get(group)
        if not isinstance(mapping, dict) or not mapping:
            raise CoverageError(f"Missing routing group {group}")
        for key, route in mapping.items():
            paths = route.get("load") if isinstance(route, dict) else None
            if not isinstance(paths, list):
                raise CoverageError(f"Invalid route {group}.{key}")
            for p in paths:
                if not isinstance(p, str):
                    raise CoverageError(f"Non-path in {group}.{key}")
                routed.add(p)
    all_paths = required | routed
    for p in sorted(all_paths):
        if (p.startswith(EXCLUDED_PREFIXES) or p.startswith("/") or "\\\\" in p
                or ".." in Path(p).parts):
            raise CoverageError(f"Forbidden active route {p}")
        resolved = (root / p).resolve()
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise CoverageError(f"Invalid route path {p}")

    missing = sorted(active - all_paths)
    if missing:
        raise CoverageError(f"UNREACHABLE_ACTIVE_RULE: {missing}")
    stage = router["stage_routes"]
    if set(stage) != {"L0_BOOTSTRAP", "L1_SOURCE_CENSUS",
                      "L2_GEOMETRY", "L3_VALIDATE_EXPORT_QA"}:
        raise CoverageError("Mandatory E2E stage set is incomplete")
    for key in ("L2_GEOMETRY", "L3_VALIDATE_EXPORT_QA"):
        if not stage[key]["load"]:
            raise CoverageError(f"Critical stage has no mandatory rule: {key}")

    # Coverage map may reference regression evidence for history; do not
    # reinterpret those paths as authority, but do not permit broken pointers.
    missing_refs = []
    for release, info in coverage.get("release_coverage", {}).items():
        for kind in ("active", "regression"):
            for p in info.get(kind, []):
                if not (root / p).is_file():
                    missing_refs.append((release, kind, p))
    if missing_refs:
        raise CoverageError(f"Broken release coverage/evidence references: {missing_refs}")

    return {
        "status": "PASS",
        "release": router["release"],
        "active_module_count": len(active),
        "routed_active_module_count": len(active & all_paths),
        "unreachable_active_modules": [],
        "active_modules": sorted(active),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = audit(args.repo_root)
    except (CoverageError, OSError, KeyError, yaml.YAMLError) as exc:
        print(f"RULE_COVERAGE_FAIL: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
