#!/usr/bin/env python3
"""Read-only Phase 1 TrainAiCad error-catalog inspection.

Independent utility: never reads PDFs, modifies CAD, changes skill files,
records incidents, activates gates, or writes to the repository.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml

LEVELS = {"L1", "L2", "L3", "L4"}
RESPONSES = {
    0: "NO_CONFIRMED_NEW_EVENT",
    1: "ADVISORY_PLUS_REGRESSION",
    2: "MANDATORY_PREFLIGHT_EVIDENCE",
    3: "HARD_GATE_REVIEW_ONLY_IF_UNPROVEN",
    4: "SYSTEMIC_DETERMINISTIC_GUARD_OR_MANUAL_ENGINEERING_HOLD",
}
PASSIVE = {
    "auto_load_by_agent": False,
    "automatic_escalation": False,
    "exporter_or_qa_hooks": False,
    "incident_history_recording": False,
    "read_only_manual_cli": True,
}


def read_catalog(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as source:
        catalog = yaml.safe_load(source)
    if not isinstance(catalog, dict):
        raise ValueError("ERROR_INDEX must be one YAML mapping")
    return catalog


def validate(c: dict, repo_root: Path | None = None) -> dict:
    """Validate catalog structure and optionally check repo reference paths."""
    errors: list[str] = []
    warnings: list[str] = []
    families = c.get("families", {})
    routes = c.get("risk_routes", {})
    docs = c.get("regression_cases", [])
    gates = c.get("gates", {})
    if c.get("status") != "PASSIVE_INDEX_NOT_PRODUCTION_SKILL":
        errors.append("Phase 1 catalog cannot identify as a production skill")
    if c.get("phase1_integration") != PASSIVE:
        errors.append("Phase 1 integration MUST remain passive and read-only")
    authority = c.get("authority", {})
    if not authority.get("new_lesson_requires_direct_user_approval"):
        errors.append("Missing direct user approval boundary")
    if not authority.get("legacy_superseded_fragments_never_override_current_skill"):
        errors.append("Missing CURRENT production skill precedence")
    if not authority.get("unknown_customer_dimension_may_not_be_filled_from_regression"):
        errors.append("A regression cannot fill unproved source dimensions")
    if not isinstance(families, dict) or not families:
        errors.append("No failure families")
        families = {}
    if not isinstance(routes, dict):
        errors.append("Risk routes must be a mapping")
        routes = {}
    if not isinstance(docs, list):
        errors.append("Regression registry must be an array")
        docs = []
    if not isinstance(gates, dict) or not gates:
        errors.append("Existing-gate descriptions are missing")
        gates = {}

    coverage = {family: 0 for family in families}
    for family, data in families.items():
        if not isinstance(data, dict):
            errors.append(f"{family}: invalid family record")
            continue
        if data.get("baseline_severity") not in LEVELS:
            errors.append(f"{family}: unknown severity")
        if not data.get("gate_ids") or any(g not in gates for g in data["gate_ids"]):
            errors.append(f"{family}: missing or unknown existing gate")
        if data.get("historical_incidents_confirmed", False) is not None:
            errors.append(f"{family}: cannot invent historical recurrence counts")
        if data.get("new_incidents", []) != []:
            errors.append(f"{family}: Phase 1 may not store new incidents")
        if data.get("recurrence_since_catalog") != 0:
            errors.append(f"{family}: Phase 1 may not increment recurrence")
        if data.get("production_escapes_since_catalog") != 0:
            errors.append(f"{family}: Phase 1 may not increment escapes")
        for tag in data.get("risk_tags", []):
            if family not in routes.get(tag, []):
                errors.append(f"{family}: missing reverse risk route for {tag}")

    for tag, assigned in routes.items():
        if not isinstance(assigned, list) or not assigned:
            errors.append(f"{tag}: empty risk route")
            continue
        if any(f not in families for f in assigned):
            errors.append(f"{tag}: undefined failure family")

    seen: set[str] = set()
    for doc in docs:
        if not isinstance(doc, dict):
            errors.append("Malformed regression record")
            continue
        path = doc.get("path", "")
        valid_path = (isinstance(path, str) and path.startswith("regression/")
                      and path.endswith(".md") and ".." not in Path(path).parts
                      and not path.endswith("/README.md"))
        if not valid_path:
            errors.append(f"Invalid regression path: {path}")
            continue
        if path in seen:
            errors.append(f"Duplicate regression document: {path}")
        seen.add(path)
        if repo_root is not None and not (repo_root / path).is_file():
            errors.append(f"Missing referenced regression: {path}")
        if "LEGACY" in doc.get("scope", "") and not doc.get("precedence_notes"):
            errors.append(f"Legacy regression must specify current-rule precedence: {path}")
        if doc.get("scope") == "HISTORICAL_OPT_IN_V4_7" and not doc.get("precedence_notes"):
            errors.append(f"Historical export needs opt-in precedence notes: {path}")
        scenarios = doc.get("scenarios", [])
        if not isinstance(scenarios, list) or not scenarios:
            errors.append(f"No scenarios: {path}")
            continue
        for scenario in scenarios:
            if not isinstance(scenario, dict) or not scenario.get("case_id") or not scenario.get("regression_target"):
                errors.append(f"Invalid scenario in {path}")
                continue
            mapped = scenario.get("families", [])
            if not mapped:
                errors.append(f"Scenario has no failure family in {path}")
            for family in mapped:
                if family not in families:
                    errors.append(f"Undefined family {family} in {path}")
                else:
                    coverage[family] += 1
    for family, count in coverage.items():
        if count == 0:
            errors.append(f"No regression example supports family {family}")
    if c.get("event_policy", {}).get("historical_production_escape_state") != "UNKNOWN_NOT_ASSUMED_ZERO":
        errors.append("Historical released-production escapes must remain unknown")
    return {
        "valid": not errors, "error_count": len(errors), "errors": errors,
        "warnings": warnings, "families": len(families),
        "source_docs": len(docs),
        "scenarios": sum(len(d.get("scenarios", [])) for d in docs if isinstance(d, dict)),
        "mapped_scenarios_by_family": coverage,
    }


def route(c: dict, risk_tags: list[str], historical_opt_in: bool = False) -> dict:
    """Manual hypothetical document retrieval; does NOT control Codex or QA."""
    families = set()
    for tag in risk_tags:
        families.update(c["risk_routes"].get(tag, []))
    references = []
    precedence = set()
    for record in c["regression_cases"]:
        matched = sorted(families & {
            family for scenario in record["scenarios"] for family in scenario["families"]
        })
        if not matched:
            continue
        if record["scope"] == "HISTORICAL_OPT_IN_V4_7" and not historical_opt_in:
            continue
        references.append({
            "path": record["path"], "scope": record["scope"],
            "matched_families": matched,
        })
        precedence.update(record.get("precedence_notes", []))
    gates = sorted({
        gate for family in families for gate in c["families"][family]["gate_ids"]
    })
    return {
        "risk_tags": risk_tags,
        "unrecognized_tags": sorted(set(risk_tags) - c["risk_routes"].keys()),
        "selected_families": sorted(families),
        "required_gates_from_existing_rules": gates,
        "regression_documents": references,
        "precedence_warnings": sorted(precedence),
        "note": "MANUAL PREVIEW ONLY; no automatic CAD routing. Old cases cannot fill missing PDF dimensions.",
    }


def escalate(c: dict, family: str, confirmed_events: int, production_escapes: int = 0) -> dict:
    """Pure simulation of proposed escalation; does not change state."""
    if family not in c["families"]:
        raise ValueError(f"Unknown failure family: {family}")
    if confirmed_events < 0 or production_escapes < 0:
        raise ValueError("Counts must be non-negative")
    if production_escapes > confirmed_events:
        raise ValueError("An escape must be part of independently confirmed incidents")
    response = RESPONSES[min(4, confirmed_events)]
    if production_escapes and confirmed_events < 4:
        response = "HARD_GATE_AND_ENGINEERING_ROOT_CAUSE_REVIEW"
    data = c["families"][family]
    return {
        "family": family, "baseline_severity": data["baseline_severity"],
        "effective_severity": "L4" if production_escapes else data["baseline_severity"],
        "confirmed_events": confirmed_events,
        "released_production_escapes": production_escapes,
        "proposed_additional_enforcement": response,
        "existing_skill_gates_remain_mandatory": data["gate_ids"],
        "mandatory_evidence": data["source_evidence_required"],
        "caution": "SIMULATION ONLY. No events were logged and no release gate was activated.",
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path,
                        default=repo_root / "regression/error_catalog/ERROR_INDEX.yaml")
    commands = parser.add_subparsers(dest="command", required=True)
    validation = commands.add_parser("validate", help="Read-only schema and reference-path audit")
    validation.add_argument("--repo", type=Path)
    preflight = commands.add_parser("preflight", help="Manual hypothetical routing only")
    preflight.add_argument("--tags", nargs="+", required=True)
    preflight.add_argument("--historical-dual-export", action="store_true")
    escalation = commands.add_parser("escalate", help="Manual simulation; no live enforcement")
    escalation.add_argument("--family", required=True)
    escalation.add_argument("--confirmed-events", type=int, required=True)
    escalation.add_argument("--production-escapes", type=int, default=0)
    args = parser.parse_args()
    catalog = read_catalog(args.index)
    if args.command == "validate":
        output = validate(catalog, args.repo)
    elif args.command == "preflight":
        output = route(catalog, args.tags, args.historical_dual_export)
    else:
        output = escalate(catalog, args.family, args.confirmed_events,
                          args.production_escapes)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if args.command != "validate" or output["valid"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, yaml.YAMLError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(2)
