#!/usr/bin/env python3
"""Benchmark source-grounded per-code routing I/O, not manufacturing accuracy.

Byte counts are exact for pinned repo files. Token counts, if tiktoken is
installed, are explicitly cl100k_base estimates, not a promise of GPT tokens.
The complete L0-L3 union still MUST be consumed through the E2E pipeline.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from audit_rule_coverage import ROOT, ROUTER, audit
from resolve_rules import resolve_rules


def _scenario(router: dict, name: str) -> dict:
    state = "UNKNOWN" if name == "unknown_complex" else "NO"
    features = {k: {"state": state} for k in router["feature_routes"]}
    scenarios = {
        "flat": ("PDF_ONLY", "FLAT_NO_BEND", "NO", []),
        "flat_tap": ("PDF_ONLY", "FLAT_NO_BEND", "NO", ["HOLE", "TAP"]),
        "bend_nobi": ("PDF_ONLY", "BEND", "NO", ["HOLE", "NOBI"]),
        "data_holes": ("PDF_DATA_RAW", "FLAT_NO_BEND", "NO", ["HOLE"]),
        "unknown_complex": ("PDF_DATA_RAW", "UNKNOWN", "UNKNOWN", []),
    }
    src, mode, reference, selected = scenarios[name]
    for x in selected:
        features[x]["state"] = "YES"
    return {"source_mode": src, "part_mode": mode,
            "reference_present": reference, "features": features}


def benchmark(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    audit(root)
    router = yaml.safe_load((root / ROUTER).read_text(encoding="utf-8"))
    cases = []
    for name in ("flat", "flat_tap", "bend_nobi", "data_holes", "unknown_complex"):
        plan = resolve_rules(_scenario(router, name), root, router)
        stages = plan["stage_plans"]
        first_bytes = sum(stages[stage]["new_bytes"]
                          for stage in ("L0_BOOTSTRAP", "L1_SOURCE_CENSUS"))
        full_bytes = plan["new_bytes_total"]
        # Initial-stage savings are the gain from not loading all eventual
        # CAD rules before the actual source/census phase. The full job has
        # no claimed total-token savings unless deduplication removes rules.
        initial_reduction = (1 - first_bytes / full_bytes) * 100
        cases.append({
            "scenario": name,
            "first_two_stages_bytes": first_bytes,
            "all_stages_unique_bytes": full_bytes,
            "initial_context_reduction_pct_vs_eager_load": round(initial_reduction, 2),
            "stage_breakdown": {k: stages[k]["new_bytes"] for k in plan["stage_order"]},
            "route_count": len(plan["rule_paths"]),
        })
    return {
        "release": router["release"],
        "metric": "EXACT_UTF8_BYTES_NOT_LLM_TOKENS",
        "baseline_branch": "archive/pr24-pre-token-optimization-20261012",
        "stage_invariant": "L0_L1_L2_L3_ALL_MANDATORY",
        "cases": cases,
        "note": ("Full-job cumulative context may be close to previous eager "
                 "loading; savings shown are startup/stage-specific only."),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(benchmark(args.repo_root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
