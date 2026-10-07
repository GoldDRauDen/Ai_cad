from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_views_only_requires_complete_source_view_fallback():
    guard = load(ROOT / "tools/holistic_engineering_guard.py", "hg1")
    part = {
        "status": "VIEWS_ONLY",
        "source_exhausted": True,
        "holistic_challenge_run": True,
        "proved_source_view_member_ids": ["a", "b"],
        "views_only_canonical_member_ids": ["a"],
    }
    assert "VIEWS_ONLY_SOURCE_VIEW_COMPLETENESS" in guard.part_anomalies(part)


def test_bend_edge_semantic_reuse_is_rejected():
    guard = load(ROOT / "tools/holistic_engineering_guard.py", "hg2")
    part = {
        "dimensions": [{
            "semantic": "SHARED_BEND_EDGE_LENGTH",
            "used_as": ["FLAT_BLANK_EXTENT"],
            "same_physical_parameter_proved": False,
        }]
    }
    assert "BEND_EDGE_USED_AS_BLANK_EXTENT" in guard.part_anomalies(part)


def test_part_identity_collision_is_rejected():
    guard = load(ROOT / "tools/holistic_engineering_guard.py", "hg3")
    job = {"parts": [
        {"code": "A", "complete_source_bundle_id": "bundle"},
        {"code": "B", "complete_source_bundle_id": "bundle"},
    ]}
    assert guard.identity_collisions(job["parts"]) == ["PART_IDENTITY_COLLISION:bundle"]


def test_reference_only_upgrade_is_not_source_proof():
    fw = load(ROOT / "tools/reference_exposure_guard.py", "rf1")
    before = fw.freeze_snapshot({"claims": [
        {"claim_id": "x", "status": "UNKNOWN", "evidence_provenance": ["PRINTED"], "evidence_keys": ["pdf:x"]}
    ]})
    after = {"claims": [
        {"claim_id": "x", "status": "PROVED", "evidence_provenance": ["PRINTED", "APPROVED_REFERENCE"], "evidence_keys": ["pdf:x"]}
    ]}
    assert "POST_REFERENCE_SOURCE_REWRITE:x" in fw.audit_transition(before, after)


def test_sample_flag_stays_pending():
    fw = load(ROOT / "tools/reference_exposure_guard.py", "rf2")
    before = fw.freeze_snapshot({"claims": [
        {"claim_id": "r", "status": "CUSTOMER_CONFIRMATION_PENDING", "sample_flagged": True}
    ]})
    after = {"claims": [
        {"claim_id": "r", "status": "PROVED", "evidence_provenance": ["APPROVED_REFERENCE"], "sample_flagged": True}
    ]}
    assert "SAMPLE_FLAGGED_PROMOTED_TO_PROVED:r" in fw.audit_transition(before, after)


def test_v433_workflow_runs_regression():
    wf = (ROOT / ".github/workflows/dxf-export-tests.yml").read_text(encoding="utf-8")
    assert "V4.19-V4.33" in wf
    assert "check_521007_07_v433.py" in wf
