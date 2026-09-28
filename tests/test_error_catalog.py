"""Phase 1 passive error-catalog metadata and simulation tests.

These tests DO NOT verify PDF interpretation or manufacturing DXF correctness.
"""
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from error_catalog import read_catalog, validate, route, escalate  # noqa: E402

CATALOG = read_catalog(ROOT / "regression/error_catalog/ERROR_INDEX.yaml")


def test_schema_and_all_referenced_regression_documents_exist():
    result = validate(CATALOG, ROOT)
    assert result["valid"], result["errors"]
    assert result["families"] == 12
    assert result["source_docs"] == 12
    assert result["scenarios"] == 58


def test_datum_preflight_routes_to_existing_approved_case():
    result = route(CATALOG, ["ABSOLUTE_ORDINATE"])
    assert "DATUM_FRAME" in result["selected_families"]
    assert "G_DATUM" in result["required_gates_from_existing_rules"]
    assert any("043793" in doc["path"] for doc in result["regression_documents"])
    assert all(doc["scope"] != "HISTORICAL_OPT_IN_V4_7"
               for doc in result["regression_documents"])


def test_historical_dual_export_only_when_explicitly_requested():
    ordinary = route(CATALOG, ["COMPOSITE_EXPORT"])
    historical = route(CATALOG, ["COMPOSITE_EXPORT"], historical_opt_in=True)
    assert not any(doc["scope"] == "HISTORICAL_OPT_IN_V4_7"
                   for doc in ordinary["regression_documents"])
    assert any(doc["scope"] == "HISTORICAL_OPT_IN_V4_7"
               for doc in historical["regression_documents"])


def test_recurrence_and_production_escape_are_only_proposals():
    get = lambda events, escapes=0: escalate(CATALOG, "DIM_WITNESS_ENDPOINT", events, escapes)
    assert get(1)["proposed_additional_enforcement"] == "ADVISORY_PLUS_REGRESSION"
    assert get(2)["proposed_additional_enforcement"] == "MANDATORY_PREFLIGHT_EVIDENCE"
    assert get(3)["proposed_additional_enforcement"] == "HARD_GATE_REVIEW_ONLY_IF_UNPROVEN"
    assert get(4)["proposed_additional_enforcement"].startswith("SYSTEMIC_")
    escaped = get(1, 1)
    assert escaped["effective_severity"] == "L4"
    assert escaped["proposed_additional_enforcement"] == "HARD_GATE_AND_ENGINEERING_ROOT_CAUSE_REVIEW"


def test_legacy_precedence_and_invalid_family_are_rejected():
    bad = deepcopy(CATALOG)
    bad["regression_cases"][0].pop("precedence_notes")
    assert not validate(bad)["valid"]
    bad = deepcopy(CATALOG)
    bad["regression_cases"][0]["scenarios"][0]["families"] = ["INVENTED"]
    assert not validate(bad)["valid"]


def test_unverified_history_cannot_be_invented():
    bad = deepcopy(CATALOG)
    bad["families"]["DATUM_FRAME"]["historical_incidents_confirmed"] = 3
    assert not validate(bad)["valid"]


def test_catalog_stays_passive_and_read_only():
    assert CATALOG["phase1_integration"] == {
        "auto_load_by_agent": False,
        "automatic_escalation": False,
        "exporter_or_qa_hooks": False,
        "incident_history_recording": False,
        "read_only_manual_cli": True,
    }
    assert all(f["historical_incidents_confirmed"] is None
               for f in CATALOG["families"].values())


def test_catalog_activation_or_path_traversal_fails_validation():
    activated = deepcopy(CATALOG)
    activated["phase1_integration"]["exporter_or_qa_hooks"] = True
    assert not validate(activated)["valid"]
    invalid = deepcopy(CATALOG)
    invalid["regression_cases"][0]["path"] = "regression/../skills/lispcad/core/VALIDATION.md"
    assert not validate(invalid)["valid"]


def test_simulation_rejects_impossible_counts():
    import pytest
    with pytest.raises(ValueError):
        escalate(CATALOG, "DATUM_FRAME", 0, 1)
    with pytest.raises(ValueError):
        escalate(CATALOG, "DATUM_FRAME", -1)
