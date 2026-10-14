#!/usr/bin/env python3
"""Deterministic signed witness graph, with typed endpoints and cycle closure."""
from __future__ import annotations

from collections import defaultdict, deque
from decimal import Decimal, InvalidOperation

TYPES = {"OUTER_EDGE", "CONTOUR_EDGE", "STEP", "HOLE_CENTER", "SLOT_MIDPOINT",
         "ARC_CENTER", "OUTER_TIP", "TANGENT_POINT", "CENTERLINE", "REFERENCE_DATUM"}
KINDS = {"CHAIN", "BASELINE", "LOCAL", "STEP", "ORDINATE", "OVERALL", "ASSEMBLY_OFFSET"}


class WitnessError(ValueError):
    pass


def _dec(value):
    if isinstance(value, bool):
        raise WitnessError("DIMENSION_NOT_NUMERIC")
    try:
        n = Decimal(str(value))
        if not n.is_finite():
            raise ValueError()
        return n
    except (ValueError, TypeError, InvalidOperation) as exc:
        raise WitnessError("DIMENSION_NOT_NUMERIC") from exc


def validate_graph(graph):
    if not isinstance(graph, dict):
        raise WitnessError("WITNESS_GRAPH_MISSING")
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    targets = graph.get("targets")
    if not isinstance(nodes, dict) or not isinstance(edges, list) or not isinstance(targets, list):
        raise WitnessError("WITNESS_GRAPH_INCOMPLETE")
    if any(kind not in TYPES for kind in nodes.values()):
        raise WitnessError("WITNESS_NODE_TYPE_UNKNOWN")
    adjacency = defaultdict(list)
    for edge in edges:
        try:
            start, end = edge["from_node"], edge["to_node"]
            axis = edge["axis"]
            kind = edge["kind"]
            if start not in nodes or end not in nodes or axis not in {"X", "Y"} or kind not in KINDS:
                raise WitnessError("WITNESS_NODE_OR_KIND_UNPROVED")
            proof = edge["proof"]
            if (not proof.get("pdf_page") or not proof.get("evidence_ref") or
                    proof.get("endpoint_verified") is not True or
                    proof.get("from_type") != nodes[start] or proof.get("to_type") != nodes[end]):
                raise WitnessError("WITNESS_ENDPOINT_UNPROVED")
            value = _dec(edge["value_mm"])
        except (KeyError, TypeError, AttributeError) as exc:
            raise WitnessError("WITNESS_EDGE_INCOMPLETE") from exc
        adjacency[(axis, start)].append((end, value))
        adjacency[(axis, end)].append((start, -value))
    output = {}
    for target in targets:
        try:
            origin, dest, axis = target["datum_node"], target["feature_node"], target["axis"]
            if origin not in nodes or dest not in nodes or axis not in {"X", "Y"}:
                raise WitnessError("WITNESS_TARGET_UNKNOWN")
            expected = _dec(target["coordinate_mm"])
            feature_id = target["feature_id"]
        except (KeyError, TypeError) as exc:
            raise WitnessError("WITNESS_TARGET_INCOMPLETE") from exc
        known = {origin: Decimal("0")}
        todo = deque([origin])
        while todo:
            node = todo.popleft()
            for neighbor, delta in adjacency[(axis, node)]:
                position = known[node] + delta
                if neighbor in known:
                    if abs(position - known[neighbor]) > Decimal("0.0000001"):
                        raise WitnessError("DIMENSION_CHAIN_CONFLICT")
                else:
                    known[neighbor] = position
                    todo.append(neighbor)
        if dest not in known:
            raise WitnessError("DIMENSION_CHAIN_DISCONNECTED")
        if abs(known[dest] - expected) > Decimal("0.0000001"):
            raise WitnessError("DIMENSION_CHAIN_MISMATCH")
        output[(feature_id, axis)] = known[dest]
    return output


def validate_part_witnesses(part):
    required = part.get("witness_required_feature_ids", [])
    graph = part.get("feature_witness_graph")
    if required and graph is None:
        raise WitnessError("WITNESS_GRAPH_MISSING")
    if graph is None:
        return {}
    solved = validate_graph(graph)
    for feature in required:
        for axis in ("X", "Y"):
            if (feature, axis) not in solved:
                raise WitnessError(f"WITNESS_REQUIRED_AXIS_MISSING:{feature}:{axis}")
    return solved
