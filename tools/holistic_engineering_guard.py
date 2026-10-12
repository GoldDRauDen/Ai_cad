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


# Source-to-canonical checks used by the normal V4.31 production exporter.
# These check actual ledger relationships, not caller-supplied success booleans.
# Full source extraction still happens upstream; no DXF can prove that an
# omitted PDF note was read in the first place.
def _active_family(part: Dict[str, Any], family: str) -> bool:
    return any(
        g.get("family") == family and g.get("status") != "CANCELED"
        for g in part.get("source_groups", [])
    )


def _note_family(note: Dict[str, Any]) -> str | None:
    family = note.get("candidate_family") or note.get("family")
    if isinstance(family, str) and family:
        return family.upper()
    text = str(note.get("text", note.get("note_text", ""))).upper()
    if "KEGAKI" in text or "ケガキ" in text or "罫書" in text:
        return "KEGAKI"
    return None


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    v = float(value)
    from math import isfinite
    return v if isfinite(v) else None


def canonical_job_anomalies(job: Dict[str, Any]) -> List[str]:
    """Validate source-note ownership, mark/bend family identity and OD chains.

    The canonical contract handles member counts/IDs and DXF read-back handles
    exact serialized geometry. This function closes their semantic gap using
    source evidence already retained in the job. Evidence not captured by the
    reader must still be caught by an independent source census / reverse QA.
    """
    parts = job.get("parts", [])
    by_code = {str(p.get("code")): p for p in parts}
    out: List[str] = []
    for part in parts:
        code = str(part.get("code", "?"))
        groups = part.get("source_groups", [])
        entity_by_id = {
            e.get("entity_id"): e for e in part.get("entities", [])
            if e.get("entity_id")
        }
        members_by_group: Dict[str, List[Dict[str, Any]]] = {}
        for member in part.get("canonical_members", []):
            if member.get("origin") == "SOURCE":
                members_by_group.setdefault(str(member.get("group_id")), []).append(member)

        for note in part.get("source_manufacturing_notes", []):
            family = _note_family(note)
            if not family:
                continue
            resolution = str(note.get("resolution", "")).upper()
            if resolution in {"CANCELLED", "CANCELED", "IRRELEVANT_TO_MANUFACTURING"}:
                continue
            target = str(note.get("target_code", "")).strip()
            assigned_away = resolution.startswith("ASSIGNED_TO_") or (
                bool(target) and target != code
            )
            if assigned_away:
                if _active_family(part, family):
                    out.append(f"{code}:SOURCE_NOTE_HOST_OWNERSHIP_CONFLICT:{family}")
                if target:
                    if target not in by_code or not _active_family(by_code[target], family):
                        out.append(f"{code}:SOURCE_NOTE_TARGET_FAMILY_MISSING:{family}:{target}")
                continue
            if resolution in {"UNRESOLVED", "UNKNOWN"} and part.get("status") == "PASS":
                out.append(f"{code}:UNRESOLVED_SOURCE_MANUFACTURING_NOTE:{family}")
            if not _active_family(part, family):
                out.append(f"{code}:SOURCE_NOTE_TO_FAMILY_MISSING:{family}")

        for group in groups:
            family = str(group.get("family", "")).upper()
            if family not in {"KEGAKI", "BEND"} or group.get("status") == "CANCELED":
                continue
            gid = str(group.get("group_id"))
            owned = [
                entity_by_id[eid]
                for member in members_by_group.get(gid, [])
                for eid in member.get("entity_ids", [])
                if eid in entity_by_id
            ]
            expected_role = "kegaki" if family == "KEGAKI" else "bend"
            if any(e.get("role") != expected_role for e in owned):
                out.append(f"{code}:CANONICAL_FAMILY_ENTITY_ROLE_MISMATCH:{gid}")
            if group.get("status") == "PROVED" and not owned:
                out.append(f"{code}:SOURCE_GROUP_HAS_NO_PHYSICAL_ENTITIES:{gid}")
            if family == "BEND" and group.get("status") == "PROVED":
                if len(owned) != 2 or any(
                    e.get("type") != "LINE" or e.get("linetype") != "DASHED"
                    for e in owned
                ):
                    out.append(f"{code}:BEND_PAIR_SOURCE_GROUP_MISMATCH:{gid}")
            if family == "KEGAKI" and group.get("status") == "PROVED":
                if any(e.get("type") != "LINE" or e.get("color") != 1 for e in owned):
                    out.append(f"{code}:KEGAKI_SOURCE_GROUP_GEOMETRY_MISMATCH:{gid}")

        # Optional per-bend source arithmetic: never accept a hardcoded
        # 'flat_attempted=True' when actual witness arithmetic is supplied.
        for i, bend in enumerate(part.get("per_bend_witness_ledger", [])):
            label = str(bend.get("bend_id", i))
            od = bend.get("od_actual_mm")
            nobi = _numeric(bend.get("nobi_mm"))
            flat = _numeric(bend.get("flat_mm"))
            pair = bend.get("bend_pair_mm")
            if (not isinstance(od, list) or len(od) != 2 or
                    any(_numeric(x) is None for x in od) or
                    nobi is None or flat is None or
                    not isinstance(pair, list) or len(pair) != 2 or
                    any(_numeric(x) is None for x in pair)):
                out.append(f"{code}:BEND_WITNESS_LEDGER_INCOMPLETE:{label}")
                continue
            a, b = (float(x) for x in od)
            y1, y2 = (float(x) for x in pair)
            if abs(a + b - nobi - flat) > 0.011 or (
                abs((y2 - y1) - nobi) > 0.011
            ) or abs(y2 - a) > 0.011:
                out.append(f"{code}:BEND_OD_NOBI_CLOSURE_FAIL:{label}")
            group_ids = {
                g.get("group_id") for g in groups
                if g.get("family") == "BEND" and g.get("status") == "PROVED"
            }
            if bend.get("source_group_id") not in group_ids:
                out.append(f"{code}:BEND_WITNESS_SOURCE_GROUP_MISSING:{label}")

        # Optional explicit FACE_GRAPH candidate ledger; booleans do not
        # constitute proof of source exhaustion.
        if part.get("status") == "VIEWS_ONLY" and (
            part.get("source_exhausted") is True or
            part.get("holistic_challenge_run") is True
        ):
            candidates = part.get("face_graph_candidates")
            unresolved = part.get("unresolved_objects")
            if (not isinstance(candidates, list) or not candidates or
                    any(not isinstance(c, dict) or
                        not {"candidate_id", "constraint_result", "evidence_used"} <= set(c)
                        for c in candidates) or
                    not isinstance(unresolved, list) or not unresolved):
                out.append(f"{code}:VIEWS_ONLY_SOURCE_EXHAUSTION_UNPROVED")

    return sorted(set(out))
