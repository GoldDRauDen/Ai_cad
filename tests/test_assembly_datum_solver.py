"""Regression for indirect assembly datums, never reference-DXF coordinate fitting."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "regression/datum/521013-04_059636_assembly_graph.json"


def solver():
    spec = importlib.util.spec_from_file_location(
        "assembly_datum_solver", ROOT / "tools/assembly_datum_solver.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def source_graph():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_059636_assembly_chain_proves_20_not_25():
    m = solver()
    result = m.solve_relative(source_graph(), "F_BOTTOM", "F_M6_CENTER", "Y")
    assert result["status"] == "PROVED"
    assert result["offset_mm"] == "20"
    assert len(result["witness_path"]) == 4
    assert all(step["source_ref"].startswith("USER_CONFIRMED:") for step in result["witness_path"])
    assert result["offset_mm"] != "25"


def test_reversed_datum_sign_is_preserved():
    m = solver()
    result = m.solve_relative(source_graph(), "F_M6_CENTER", "F_BOTTOM", "Y")
    assert result["offset_mm"] == "-20"


def test_059636_rejects_25_as_conflicting_assumed_dimension():
    m = solver()
    graph = source_graph()
    graph["constraints"].append({
        "edge_id": "INCORRECT_25",
        "from": "F_BOTTOM",
        "to": "F_M6_CENTER",
        "axis": "Y",
        "delta_mm": "25",
        "frame_id": graph["frame_id"],
        "status": "PROVED",
        "dimension_type": "LOCAL",
        "source_ref": "USER_CONFIRMED:synthetic-wrong-value",
        "witness_from": "F bottom",
        "witness_to": "F M6 center",
    })
    with pytest.raises(m.DatumSolveError, match="DIMENSION_CONFLICT"):
        m.solve_relative(graph, "F_BOTTOM", "F_M6_CENTER", "Y")


def test_disconnected_or_flagged_relation_does_not_guess():
    m = solver()
    graph = source_graph()
    graph["constraints"][2]["status"] = "FLAGGED"
    with pytest.raises(m.DatumSolveError, match="NO_PROVED_ASSEMBLY_DATUM_PATH"):
        m.solve_relative(graph, "F_BOTTOM", "F_M6_CENTER", "Y")


@pytest.mark.parametrize("field,value,message", [
    ("source_ref", "SAMPLE_DXF:521013-04", "NO_SOURCE_WITNESS_OR_REFERENCE_ONLY"),
    ("witness_from", "", "WITNESS_ENDPOINT_IDENTITY_MISSING"),
    ("frame_id", "DIFFERENT_VIEW", "UNPROVED_COORDINATE_FRAME_TRANSFORM"),
    ("dimension_type", "UNCLASSIFIED", "UNCLASSIFIED_DIMENSION"),
])
def test_source_evidence_frame_and_endpoint_gates(field, value, message):
    m = solver()
    graph = source_graph()
    graph["constraints"][0][field] = value
    with pytest.raises(m.DatumSolveError, match=message):
        m.solve_relative(graph, "F_BOTTOM", "F_M6_CENTER", "Y")


def test_orthogonal_axis_cannot_replace_a_missing_y_witness():
    m = solver()
    graph = source_graph()
    graph["constraints"][2]["axis"] = "X"
    with pytest.raises(m.DatumSolveError, match="NO_PROVED_ASSEMBLY_DATUM_PATH"):
        m.solve_relative(graph, "F_BOTTOM", "F_M6_CENTER", "Y")


def test_consistent_redundant_dimension_keeps_solution():
    m = solver()
    graph = source_graph()
    graph["constraints"].append({
        "edge_id": "CONFIRM_20",
        "from": "F_BOTTOM",
        "to": "F_M6_CENTER",
        "axis": "Y",
        "delta_mm": "20",
        "frame_id": graph["frame_id"],
        "status": "PROVED",
        "dimension_type": "LOCAL",
        "source_ref": "PDF:synthetic-confirmation",
        "witness_from": "F bottom",
        "witness_to": "F M6 center",
    })
    assert m.solve_relative(graph, "F_BOTTOM", "F_M6_CENTER", "Y")["offset_mm"] == "20"


def test_reject_fabricated_contact_offset():
    m = solver()
    graph = source_graph()
    graph["constraints"][1]["dimension_type"] = "CONTACT"
    with pytest.raises(m.DatumSolveError, match="NONZERO_CONTACT_OFFSET_UNPROVED"):
        m.solve_relative(graph, "F_BOTTOM", "F_M6_CENTER", "Y")


def test_reject_bad_number_and_unowned_node():
    m = solver()
    graph = source_graph()
    graph["constraints"][1]["delta_mm"] = "nan"
    with pytest.raises(m.DatumSolveError, match="non-finite"):
        m.solve_relative(graph, "F_BOTTOM", "F_M6_CENTER", "Y")
    graph = source_graph()
    del graph["nodes"]["G_M6_CENTER"]["part_id"]
    with pytest.raises(m.DatumSolveError, match="NODE_IDENTITY_UNPROVED"):
        m.solve_relative(graph, "F_BOTTOM", "F_M6_CENTER", "Y")


def test_flat_without_assembly_evidence_is_not_forced_to_use_assembly_solver():
    """The tool has no global effect: run it only for actual assembly dimension chains."""
    guard_spec = importlib.util.spec_from_file_location(
        "holistic_guard_for_assembly_test", ROOT / "tools/holistic_engineering_guard.py"
    )
    g = importlib.util.module_from_spec(guard_spec)
    assert guard_spec and guard_spec.loader
    guard_spec.loader.exec_module(g)
    assert "ASSEMBLY_DATUM_TRACE_NOT_ATTEMPTED" not in g.part_anomalies({
        "code": "unrelated-flat",
        "part_mode": "FLAT_NO_BEND",
    })
