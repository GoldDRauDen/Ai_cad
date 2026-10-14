#!/usr/bin/env python3
"""V4.33 holistic engineering challenge helpers.

This checker consumes semantic records produced by the source solver. It does not
infer CAD geometry from counts; it detects contradictions that require the solver
to reopen the source before canonical serialization.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List



def _assembly_datum_anomalies(part: Dict[str, Any]) -> List[str]:
    """Independently re-solve declared cross-part derived-feature candidates.

    Optional for single-part jobs. When source census reports an indirect
    assembly candidate, an unattempted or unverified trace cannot count as PASS.
    """
    candidates = part.get("assembly_indirect_candidates", [])
    if not candidates:
        return []
    if not isinstance(candidates, list):
        return ["ASSEMBLY_DATUM_CANDIDATE_LEDGER_INVALID"]
    traces = part.get("assembly_datum_traces", [])
    if not isinstance(traces, list):
        return ["ASSEMBLY_DATUM_TRACE_NOT_ATTEMPTED"]
    by_id = {t.get("feature_id"): t for t in traces if isinstance(t, dict)}
    if not by_id:
        return ["ASSEMBLY_DATUM_TRACE_NOT_ATTEMPTED"]

    # Loading here avoids making unrelated flat/older jobs pay solver overhead.
    import importlib.util
    from decimal import Decimal, InvalidOperation
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "assembly_datum_solver_for_qa",
        Path(__file__).with_name("assembly_datum_solver.py"),
    )
    if spec is None or spec.loader is None:
        return ["ASSEMBLY_DATUM_SOLVER_NOT_AVAILABLE"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    errors: List[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("ASSEMBLY_DATUM_CANDIDATE_LEDGER_INVALID")
            continue
        feature_id = candidate.get("feature_id")
        if not isinstance(feature_id, str) or not feature_id or feature_id in seen:
            errors.append("ASSEMBLY_DATUM_CANDIDATE_LEDGER_INVALID")
            continue
        seen.add(feature_id)
        trace = by_id.get(feature_id)
        if not trace or not isinstance(trace.get("graph"), dict):
            errors.append(f"ASSEMBLY_DATUM_TRACE_NOT_ATTEMPTED:{feature_id}")
            continue
        try:
            solved = module.solve_relative(
                trace["graph"],
                candidate["datum_node"],
                candidate["target_node"],
                candidate["axis"],
            )
        except (module.DatumSolveError, KeyError, TypeError) as exc:
            if trace.get("status") != "FLAGGED" or not trace.get("reason"):
                errors.append(f"ASSEMBLY_DATUM_UNPROVED:{feature_id}")
            continue

        if trace.get("status") != "PROVED":
            errors.append(f"DERIVABLE_ASSEMBLY_COORDINATE_FLAGGED:{feature_id}")
            continue
        try:
            claimed = Decimal(str(trace["offset_mm"]))
            actual = Decimal(solved["offset_mm"])
        except (KeyError, InvalidOperation, TypeError):
            errors.append(f"ASSEMBLY_DATUM_RESULT_MISSING:{feature_id}")
            continue
        if not claimed.is_finite() or claimed != actual:
            errors.append(f"ASSEMBLY_DATUM_RESULT_MISMATCH:{feature_id}")
        if not solved["witness_path"]:
            errors.append(f"ASSEMBLY_DATUM_WITNESS_PATH_MISSING:{feature_id}")
    return sorted(set(errors))


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

    out.extend(_assembly_datum_anomalies(part))
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
        from dimension_witness import WitnessError, validate_part_witnesses
        from slot_anchor import SlotAnchorError, validate_slot_anchor
        try:
            validate_part_witnesses(part)
        except WitnessError as exc:
            out.append(f"{code}:{exc}")
        for target in part.get("feature_witness_graph", {}).get("targets", []):
            entity_id = target.get("entity_id")
            if entity_id:
                found = next((e for e in part.get("entities", []) if e.get("entity_id") == entity_id), None)
                axis = target.get("axis")
                if not found or found.get("type") != "CIRCLE" or axis not in {"X", "Y"}:
                    out.append(f"{code}:WITNESS_ENTITY_UNPROVED:{entity_id}")
                elif abs(float(found["center"][0 if axis == "X" else 1]) - float(target["coordinate_mm"])) > 1e-7:
                    out.append(f"{code}:WITNESS_CANONICAL_COORDINATE_MISMATCH:{entity_id}")
        for record in part.get("slot_anchor_records", []):
            slot_id = record.get("slot_id", "?")
            try:
                expected = validate_slot_anchor(record)
            except SlotAnchorError as exc:
                out.append(f"{code}:{exc}:{slot_id}")
                continue
            entity_id = record.get("entity_id")
            slot_entity = next((e for e in part.get("entities", []) if e.get("entity_id") == entity_id), None)
            if (not slot_entity or slot_entity.get("role") != "slot" or
                    slot_entity.get("type") != "LWPOLYLINE" or len(slot_entity.get("vertices", [])) != 4):
                out.append(f"{code}:SLOT_CANONICAL_GEOMETRY_UNVERIFIABLE:{slot_id}")
            else:
                vertices = slot_entity["vertices"]
                mid = (sum(v[0] for v in vertices) / 4, sum(v[1] for v in vertices) / 4)
                if abs(mid[0] - expected[0]) > 1e-7 or abs(mid[1] - expected[1]) > 1e-7:
                    out.append(f"{code}:SLOT_CANONICAL_MIDPOINT_MISMATCH:{slot_id}")
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
                # One source bend may have two physical lines; a group can
                # legitimately contain several bends. Check each member.
                for member in members_by_group.get(gid, []):
                    lines = [
                        entity_by_id[eid] for eid in member.get("entity_ids", [])
                        if eid in entity_by_id
                    ]
                    if len(lines) != 2 or any(
                        e.get("type") != "LINE" or e.get("linetype") != "DASHED"
                        for e in lines
                    ):
                        out.append(f"{code}:BEND_PAIR_SOURCE_GROUP_MISMATCH:{gid}")
            if family == "KEGAKI" and group.get("status") == "PROVED":
                if any(e.get("type") != "LINE" or e.get("color") != 1 for e in owned):
                    out.append(f"{code}:KEGAKI_SOURCE_GROUP_GEOMETRY_MISMATCH:{gid}")

        # Independent cross-part witness re-solve is mandatory when the
        # source census declares an indirect assembly-position candidate.
        out.extend(f"{code}:{error}" for error in _assembly_datum_anomalies(part))

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
