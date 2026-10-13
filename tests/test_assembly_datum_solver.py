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


def _assembly_case(status="PROVED", offset="20", graph=None, reason=None):
    if graph is None:
        graph = source_graph()
    part = {
        "code": "059636",
        "status": "PASS" if status == "PROVED" else "VIEWS_ONLY",
        "assembly_indirect_candidates": [{
            "feature_id": "F_M6_ROW",
            "datum_node": "F_BOTTOM",
            "target_node": "F_M6_CENTER",
            "axis": "Y",
        }],
        "assembly_datum_traces": [{
            "feature_id": "F_M6_ROW",
            "status": status,
            "offset_mm": offset,
            "graph": graph,
            "reason": reason,
        }],
    }
    return part


def test_canonical_guard_recomputes_correct_assembly_offset():
    spec = importlib.util.spec_from_file_location(
        "guard_assembly_correct", ROOT / "tools/holistic_engineering_guard.py"
    )
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    assert not any("ASSEMBLY_DATUM" in x or "DERIVABLE_ASSEMBLY" in x
                   for x in g.canonical_job_anomalies({"parts": [_assembly_case()]}))


def test_canonical_guard_blocks_missing_trace_and_wrong_25():
    spec = importlib.util.spec_from_file_location(
        "guard_assembly_wrong", ROOT / "tools/holistic_engineering_guard.py"
    )
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    no_trace = _assembly_case()
    no_trace["assembly_datum_traces"] = []
    assert "059636:ASSEMBLY_DATUM_TRACE_NOT_ATTEMPTED" in (
        g.canonical_job_anomalies({"parts": [no_trace]})
    )
    wrong_25 = _assembly_case(offset="25")
    assert "059636:ASSEMBLY_DATUM_RESULT_MISMATCH:F_M6_ROW" in (
        g.canonical_job_anomalies({"parts": [wrong_25]})
    )


def test_canonical_guard_blocks_flagged_proved_chain_and_allows_true_blocker():
    spec = importlib.util.spec_from_file_location(
        "guard_assembly_flag", ROOT / "tools/holistic_engineering_guard.py"
    )
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    still_flagged = _assembly_case(status="FLAGGED", reason="not yet checked")
    assert "059636:DERIVABLE_ASSEMBLY_COORDINATE_FLAGGED:F_M6_ROW" in (
        g.canonical_job_anomalies({"parts": [still_flagged]})
    )
    no_path = source_graph()
    no_path["constraints"][2]["status"] = "FLAGGED"
    truly_flagged = _assembly_case(status="FLAGGED", graph=no_path,
                                   reason="NO_PROVED_ASSEMBLY_DATUM_PATH")
    assert not any("ASSEMBLY_DATUM" in x or "DERIVABLE_ASSEMBLY" in x
                   for x in g.canonical_job_anomalies({"parts": [truly_flagged]}))
