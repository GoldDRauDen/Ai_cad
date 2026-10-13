#!/usr/bin/env python3
"""Build a read-only one-file skill+rules handoff from the canonical modular repo.

Bundling is deterministic and never edits the canonical rules, production
files, or customer source. It does not replace execution of CAD tools.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import yaml

# This tool is also imported by tests using importlib.util.spec_from_file_location.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_rule_coverage import CoverageError, audit as audit_active_rule_coverage

ROOT = Path(__file__).resolve().parents[1]
ROUTER_PATH = "skills/lispcad/router/ROUTER.yaml"
BASE_FILES = (
    "SKILL.md",
    "AI_BOOTSTRAP.md",
    "AI_ENTRYPOINT.md",
    "skills/lispcad/router/FEATURE_CENSUS.md",
    ROUTER_PATH,
    "skills/lispcad/router/RULE_COVERAGE.yaml",
    "tools/CANONICAL_INPUT_SCHEMA_V431.md",
    "tools/DXF_INPUT_SCHEMA.md",
    "references/CUSTOMER_CAD_RULES.yaml",
)
EXCLUDED = ("skills/lispcad/portable/", "skills/lispcad/versions/",
            "docs/history/", "regression/", "services/trainaicad-mcp/")


class BundleError(ValueError):
    pass


def approved_paths(root: Path = ROOT) -> tuple[str, list[str]]:
    root = Path(root).resolve()
    # A seemingly complete bundle must not silently miss an active topology
    # or forming rule omitted from the router.
    try:
        audit_active_rule_coverage(root)
    except CoverageError as exc:
        raise BundleError(f"Missing or unsafe active rule coverage: {exc}") from exc
    router = yaml.safe_load((root / ROUTER_PATH).read_text(encoding="utf-8"))
    if not isinstance(router, dict) or router.get("production_mode") != "repo_direct":
        raise BundleError("Cannot bundle non-repo-direct Router")
    entry = (root / "AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    if router.get("release", "") not in entry:
        raise BundleError("Entrypoint and Router release mismatch")
    paths: list[str] = []
    seen = set()

    def add(p: str) -> None:
        if not isinstance(p, str) or not p or p.startswith(EXCLUDED) or (
            p.startswith("/") or "\\" in p or ".." in Path(p).parts
        ):
            raise BundleError(f"Disallowed production path: {p!r}")
        real = (root / p).resolve()
        if not real.is_relative_to(root) or not real.is_file():
            raise BundleError(f"Missing or unsafe production file: {p}")
        if p not in seen:
            seen.add(p)
            paths.append(p)

    for p in BASE_FILES:
        add(p)
    for p in router.get("default_load", []):
        add(p)
    for group in ("stage_routes", "source_routes", "mode_routes", "feature_routes", "customer_routes"):
        for route in router[group].values():
            for p in route.get("load", []):
                add(p)

    # Additional audited source-of-truth references belong in this portable
    # handoff even if not selected by a single feature route.
    return router["release"], paths


def build_bundle(root: Path = ROOT) -> str:
    root = Path(root).resolve()
    release, paths = approved_paths(root)
    records = []
    blocks = []
    for p in paths:
        data = (root / p).read_bytes()
        try:
            content = data.decode("utf-8")
        except UnicodeError as exc:
            raise BundleError(f"Non-UTF8 rule file: {p}") from exc
        digest = hashlib.sha256(data).hexdigest()
        records.append({"path": p, "sha256": digest, "bytes": len(data)})
        blocks.append(f"\n\n---\n\n<!-- BEGIN SOURCE: {p} -->\n\n"
                      + content.rstrip()
                      + f"\n\n<!-- END SOURCE: {p} -->\n")
    manifest = {"bundle_kind": "GENERATED_READ_ONLY_SNAPSHOT",
                "release": release, "files": records}
    header = (
        "# TrainAiCad — Generated E2E Rulepack\n\n"
        "**READ-ONLY SNAPSHOT. Canonical production authority is the pinned"
        " current TrainAiCad repo/Router, not historical portable rules.**\n\n"
        "Does not provide PDF vision, a CAD runtime, or manufacturing proof.\n\n"
        "## Content manifest (deterministic SHA-256)\n\n"
        "```json\n" + json.dumps(manifest, indent=2, ensure_ascii=False) +
        "\n```\n\n## Approved source modules"
    )
    return header + "".join(blocks) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        content = build_bundle(args.repo_root)
        destination = args.output.expanduser().resolve()
        # Avoid changing source-of-truth files while generating a handoff.
        root = args.repo_root.resolve()
        if destination.is_relative_to(root):
            raise BundleError("Output must be outside repository working tree")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    except (BundleError, ValueError, OSError, KeyError, yaml.YAMLError) as exc:
        print(f"RULEPACK_BUILD_FAIL: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"output": str(destination),
                      "bytes": len(content.encode("utf-8")),
                      "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
