#!/usr/bin/env python3
"""Generate a scoped RAG_INDEX.yaml view from current Router; never edit rules.

This is a deterministic manifest/resolver, not vector search or a second
independent engineering authority. Active rules remain in ROUTER.yaml.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import yaml

from audit_rule_coverage import ROOT, ROUTER, audit


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_index(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    verified = audit(root)
    router = yaml.safe_load((root / ROUTER).read_text(encoding="utf-8"))
    ignored = ("skills/lispcad/portable/", "skills/lispcad/versions/",
               "docs/history/", "services/trainaicad-mcp/")
    evidence = sorted(p.relative_to(root).as_posix()
                      for p in (root / "regression").rglob("*") if p.is_file())
    history = sorted(p.relative_to(root).as_posix() for prefix in ignored[:3]
                     for p in (root / prefix).rglob("*") if p.is_file())
    experimental = sorted(p.relative_to(root).as_posix()
                          for p in (root / "services/trainaicad-mcp").rglob("*")
                          if p.is_file())
    executable = sorted(p.relative_to(root).as_posix()
                        for prefix in ("tools", "tests")
                        for p in (root / prefix).rglob("*.py") if p.is_file())
    all_active = verified["active_modules"]
    return {
        "schema_version": 1,
        "generated_from": ROUTER,
        "release": router["release"],
        "router_sha256": _hash_file(root / ROUTER),
        "production": {
            "entrypoints": ["SKILL.md", "AI_BOOTSTRAP.md", "AI_ENTRYPOINT.md"],
            "always_on": list(router.get("default_load", [])),
            "stages": router["stage_routes"],
            "source_routes": router["source_routes"],
            "mode_routes": router["mode_routes"],
            "feature_routes": router["feature_routes"],
            "customer_routes": router["customer_routes"],
            "customer_rule_catalog": router["customer_rule_catalog"],
            "active_modules": all_active,
            "retrieval_policy": "YES_AND_UNKNOWN_LOAD; MANDATORY_L0_L1_L2_L3",
        },
        "qa_only": {
            "entrypoint": "QA_ENTRYPOINT.md",
            "policy": "EXPLICIT_REVERSE_QA_REQUEST_ONLY",
        },
        "regression_evidence": {
            "paths": evidence,
            "policy": "ON_DEMAND_CASE_LOOKUP_NOT_LIVE_RULE_OR_CUSTOMER_GEOMETRY",
        },
        "executables": {
            "paths": executable,
            "policy": "EXECUTE_WITH_RUNTIME_DO_NOT_INJECT_ALL_SOURCE_AS_RULES",
        },
        "history_audit_only": {
            "paths": history,
            "policy": "EXCLUDED_FROM_PRODUCTION_CONTEXT",
        },
        "experimental_mcp": {
            "paths": experimental,
            "policy": "RESEARCH_ONLY_NO_DEFAULT_PRODUCTION",
        },
        "forbidden_user_files": "NEVER_OPEN_READ_COPY_OR_INDEX",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        root = args.repo_root.resolve()
        target = args.output.expanduser().resolve()
        if target.is_relative_to(root):
            raise ValueError("Generated RAG_INDEX.yaml must be outside the source repo")
        document = build_index(root)
        raw = yaml.safe_dump(document, allow_unicode=True, sort_keys=False)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(raw, encoding="utf-8")
        record = {"path": str(target), "bytes": len(raw.encode("utf-8")),
                  "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                  "active_modules": len(document["production"]["active_modules"])}
    except (ValueError, OSError, KeyError, yaml.YAMLError) as exc:
        print(f"RAG_INDEX_FAIL: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
