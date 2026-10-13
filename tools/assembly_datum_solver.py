#!/usr/bin/env python3
"""Evidence-gated, axis-specific assembly dimension graph solver.

This tool solves already-proved signed dimensions. It does not read drawings,
invent mating constraints, infer a contact from paper proximity, or authorize
production CAD without face/flat transforms and independent source QA.
"""
from __future__ import annotations

import argparse
from collections import deque
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

AXES = {"X", "Y"}
KINDS = {"BASELINE", "CHAIN", "LOCAL", "ORDINATE", "CONTACT", "ASSEMBLY_OFFSET"}
SOURCE_PREFIXES = ("PDF:", "USER_CONFIRMED:")


class DatumSolveError(ValueError):
    """A missing, inconsistent or insufficiently proved assembly datum chain."""


def _amount(raw: object, field: str) -> Decimal:
    if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
        raise DatumSolveError(f"{field}: finite decimal millimetres required")
    try:
        number = Decimal(str(raw))
    except InvalidOperation as exc:
        raise DatumSolveError(f"{field}: invalid decimal") from exc
    if not number.is_finite():
        raise DatumSolveError(f"{field}: non-finite dimension")
    return number


def _fmt(value: Decimal) -> str:
    value = value.normalize()
    return format(value, "f")


def solve_relative(graph: dict, start: str, target: str, axis: str) -> dict:
    """Compute target - start in mm, or fail closed.

    Nodes are physical witness identities in ONE proved assembly reference
    frame. Directed constraints express signed (to - from) differences.
    Only PROVED, PDF- or explicitly user-confirmed relations may be traversed.
    Every reached alternative path must give the same value, including cycles.
    """
    if axis not in AXES:
        raise DatumSolveError("INVALID_AXIS: expected X or Y")
    if not isinstance(graph, dict):
        raise DatumSolveError("INVALID_GRAPH: expected object")
    frame = graph.get("frame_id")
    nodes = graph.get("nodes")
    edges = graph.get("constraints")
    if not isinstance(frame, str) or not frame.strip():
        raise DatumSolveError("FRAME_UNPROVED: assembly frame_id required")
    if not isinstance(nodes, dict) or not isinstance(edges, list):
        raise DatumSolveError("INVALID_GRAPH: nodes mapping and constraints list required")
    for key, node in nodes.items():
        if not isinstance(key, str) or not key or not isinstance(node, dict):
            raise DatumSolveError("NODE_IDENTITY_UNPROVED")
        if not node.get("part_id") or not node.get("kind"):
            raise DatumSolveError(f"NODE_IDENTITY_UNPROVED: {key}")
    if start not in nodes or target not in nodes:
        raise DatumSolveError("DATUM_OR_FEATURE_NOT_IN_GRAPH")

    neighbors: dict[str, list[tuple[str, Decimal, dict]]] = {key: [] for key in nodes}
    seen: set[str] = set()
    for edge in edges:
        if not isinstance(edge, dict):
            raise DatumSolveError("INVALID_CONSTRAINT")
        eid = edge.get("edge_id")
        if not isinstance(eid, str) or not eid or eid in seen:
            raise DatumSolveError("DUPLICATE_OR_MISSING_EDGE_ID")
        seen.add(eid)
        state = edge.get("status")
        if state not in {"PROVED", "FLAGGED", "CANCELED"}:
            raise DatumSolveError(f"{eid}: MISSING_PROOF_STATUS")
        if state != "PROVED":
            continue
        a, b = edge.get("from"), edge.get("to")
        if a not in nodes or b not in nodes or a == b:
            raise DatumSolveError(f"{eid}: INVALID_PHYSICAL_WITNESS_NODES")
        if edge.get("axis") not in AXES:
            raise DatumSolveError(f"{eid}: INVALID_AXIS")
        if edge.get("frame_id") != frame:
            raise DatumSolveError(f"{eid}: UNPROVED_COORDINATE_FRAME_TRANSFORM")
        kind = edge.get("dimension_type")
        if kind not in KINDS:
            raise DatumSolveError(f"{eid}: UNCLASSIFIED_DIMENSION")
        source = edge.get("source_ref")
        if not isinstance(source, str) or not source.startswith(SOURCE_PREFIXES):
            raise DatumSolveError(f"{eid}: NO_SOURCE_WITNESS_OR_REFERENCE_ONLY")
        if not all(isinstance(edge.get(k), str) and edge[k].strip()
                   for k in ("witness_from", "witness_to")):
            raise DatumSolveError(f"{eid}: WITNESS_ENDPOINT_IDENTITY_MISSING")
        distance = _amount(edge.get("delta_mm"), f"{eid} delta_mm")
        if kind == "CONTACT" and distance != 0:
            raise DatumSolveError(f"{eid}: NONZERO_CONTACT_OFFSET_UNPROVED")
        if edge["axis"] != axis:
            continue
        neighbors[a].append((b, distance, edge))
        neighbors[b].append((a, -distance, edge))

    potential = {start: Decimal("0")}
    parent: dict[str, tuple[str, dict, Decimal]] = {}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for other, delta, edge in neighbors[node]:
            expected = potential[node] + delta
            if other in potential:
                if potential[other] != expected:
                    raise DatumSolveError(
                        f"DIMENSION_CONFLICT: {edge['edge_id']} makes "
                        f"{other}={_fmt(expected)} vs {_fmt(potential[other])}"
                    )
                continue
            potential[other] = expected
            parent[other] = (node, edge, delta)
            queue.append(other)
    if target not in potential:
        raise DatumSolveError("NO_PROVED_ASSEMBLY_DATUM_PATH")

    path = []
    current = target
    while current != start:
        previous, edge, delta = parent[current]
        path.append({
            "edge_id": edge["edge_id"],
            "from": previous,
            "to": current,
            "signed_delta_mm": _fmt(delta),
            "source_ref": edge["source_ref"],
            "dimension_type": edge["dimension_type"],
            "witness_from": edge["witness_from"],
            "witness_to": edge["witness_to"],
        })
        current = previous
    path.reverse()
    return {
        "status": "PROVED",
        "frame_id": frame,
        "axis": axis,
        "from": start,
        "to": target,
        "offset_mm": _fmt(potential[target]),
        "witness_path": path,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Solve source-backed assembly witness chains")
    ap.add_argument("graph_json", type=Path)
    ap.add_argument("start", help="physical datum node")
    ap.add_argument("target", help="feature node")
    ap.add_argument("--axis", choices=("X", "Y"), required=True)
    ap.add_argument("--expected-mm", help="optional independent QA check")
    args = ap.parse_args()
    graph = json.loads(args.graph_json.read_text(encoding="utf-8"))
    try:
        result = solve_relative(graph, args.start, args.target, args.axis)
        if args.expected_mm is not None:
            if Decimal(result["offset_mm"]) != _amount(args.expected_mm, "expected-mm"):
                raise DatumSolveError(
                    "INDEPENDENT_QA_MISMATCH: solved="
                    + result["offset_mm"] + " expected=" + args.expected_mm
                )
    except DatumSolveError as exc:
        ap.exit(status=2, message=str(exc) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
