#!/usr/bin/env python3
"""V4.33 holistic engineering challenge helpers.

This checker consumes semantic records produced by the source solver. It does not
infer CAD geometry from counts; it detects contradictions that require the solver
to reopen the source before canonical serialization.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List


def part_anomalies(part: Dict[str, Any]) -> List[str]:
    out: List[str] = []

    physical = int(part.get("source_physical_member_count", 0))
    proved = int(part.get("proved_source_member_count", 0))
    unclassified = int(part.get("unclassified_source_member_count", 0))

    if physical > 0 and proved == 0 and not part.get("all_physical_members_drawing_only", False):
        out.append("SOURCE_MEMBER_CENSUS_GAP")
    if unclassified > 0:
        out.append("SOURCE_MEMBER_CENSUS_GAP")

    if part.get("status") == "VIEWS_ONLY":
        if not part.get("source_exhausted", False):
            out.append("VIEWS_ONLY_BEFORE_SOURCE_EXHAUSTION")
        if not part.get("holistic_challenge_run", False):
            out.append("VIEWS_ONLY_BEFORE_HOLISTIC_CHALLENGE")
        expected = set(part.get("proved_source_view_member_ids", []))
        actual = set(part.get("views_only_canonical_member_ids", []))
        if expected != actual:
            out.append("VIEWS_ONLY_SOURCE_VIEW_COMPLETENESS")
        if part.get("defensible_flat_exists", False) and part.get("only_local_uncertainty", False):
            out.append("LOCAL_UNCERTAINTY_ESCALATED_TO_VIEWS_ONLY")

    for d in part.get("dimensions", []):
        if (
            d.get("semantic") == "SHARED_BEND_EDGE_LENGTH"
            and "FLAT_BLANK_EXTENT" in set(d.get("used_as", []))
            and not d.get("same_physical_parameter_proved", False)
        ):
            out.append("BEND_EDGE_USED_AS_BLANK_EXTENT")

    if part.get("feature_family_yes_without_group", False):
        out.append("SOURCE_FEATURE_GROUP_MISSING")

    if part.get("high_source_evidence", False) and not part.get("flat_attempted", False):
        out.append("HIGH_SOURCE_EVIDENCE_WITHOUT_SOLVE_ATTEMPT")

    return sorted(set(out))


def identity_collisions(parts: Iterable[Dict[str, Any]]) -> List[str]:
    owners: Dict[str, List[Dict[str, Any]]] = {}
    for part in parts:
        bundle = part.get("complete_source_bundle_id")
        if bundle:
            owners.setdefault(str(bundle), []).append(part)

    out: List[str] = []
    for bundle, group in owners.items():
        independent = [p for p in group if not p.get("shared_assembly_view_role", False)]
        codes = {p.get("code") for p in independent}
        if len(codes) > 1:
            out.append(f"PART_IDENTITY_COLLISION:{bundle}")
    return sorted(out)


def job_anomalies(job: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for part in job.get("parts", []):
        out.extend(f"{part.get('code','?')}:{a}" for a in part_anomalies(part))
    out.extend(identity_collisions(job.get("parts", [])))
    return sorted(set(out))
