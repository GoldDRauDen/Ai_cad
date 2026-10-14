#!/usr/bin/env python3
"""V4.33 521007-07 holistic challenge and reference-exposure regression."""
from pathlib import Path
import importlib.util
import yaml


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_holistic_guard(root: Path):
    guard = load_module(root / "tools/holistic_engineering_guard.py", "holistic_guard")

    part = {
        "code": "058866",
        "source_physical_member_count": 12,
        "proved_source_member_count": 0,
        "unclassified_source_member_count": 0,
        "high_source_evidence": True,
        "flat_attempted": True,
        "dimensions": [{
            "semantic": "SHARED_BEND_EDGE_LENGTH",
            "used_as": ["BEND_EDGE_LENGTH", "FLAT_BLANK_EXTENT"],
            "same_physical_parameter_proved": False,
        }],
    }
    a = guard.part_anomalies(part)
    assert "SOURCE_MEMBER_CENSUS_GAP" in a
    assert "BEND_EDGE_USED_AS_BLANK_EXTENT" in a

    views = {
        "code": "058865",
        "status": "VIEWS_ONLY",
        "source_exhausted": False,
        "holistic_challenge_run": False,
        "proved_source_view_member_ids": ["v1", "v2", "v3"],
        "views_only_canonical_member_ids": ["v1"],
        "defensible_flat_exists": False,
    }
    a = guard.part_anomalies(views)
    assert "VIEWS_ONLY_BEFORE_SOURCE_EXHAUSTION" in a
    assert "VIEWS_ONLY_BEFORE_HOLISTIC_CHALLENGE" in a
    assert "VIEWS_ONLY_SOURCE_VIEW_COMPLETENESS" in a

    local = {
        "code": "LOCAL",
        "status": "VIEWS_ONLY",
        "source_exhausted": True,
        "holistic_challenge_run": True,
        "proved_source_view_member_ids": ["v1"],
        "views_only_canonical_member_ids": ["v1"],
        "defensible_flat_exists": True,
        "only_local_uncertainty": True,
    }
    assert "LOCAL_UNCERTAINTY_ESCALATED_TO_VIEWS_ONLY" in guard.part_anomalies(local)

    job = {"parts": [
        {"code": "058868", "complete_source_bundle_id": "DATA711"},
        {"code": "058869", "complete_source_bundle_id": "DATA711"},
    ]}
    assert "PART_IDENTITY_COLLISION:DATA711" in guard.job_anomalies(job)


def test_reference_firewall(root: Path):
    firewall = load_module(root / "tools/reference_exposure_guard.py", "reference_guard")
    before = firewall.freeze_snapshot({
        "claims": [
            {"claim_id": "attach", "status": "UNKNOWN", "evidence_provenance": ["PRINTED"], "evidence_keys": ["pdf:attach-note"]},
            {"claim_id": "sample-r", "status": "CUSTOMER_CONFIRMATION_PENDING", "sample_flagged": True},
        ]
    })
    after_bad = {
        "claims": [
            {"claim_id": "attach", "status": "PROVED", "evidence_provenance": ["PRINTED", "APPROVED_REFERENCE"], "evidence_keys": ["pdf:attach-note"]},
            {"claim_id": "sample-r", "status": "PROVED", "evidence_provenance": ["APPROVED_REFERENCE"], "sample_flagged": True},
        ]
    }
    errors = firewall.audit_transition(before, after_bad)
    assert any(x.startswith("POST_REFERENCE_SOURCE_REWRITE:attach") for x in errors)
    assert any(x.startswith("SAMPLE_FLAGGED_PROMOTED_TO_PROVED:sample-r") for x in errors)

    after_good = {
        "claims": [
            {"claim_id": "attach", "status": "REFERENCE_ASSISTED_UNDERSTANDING", "evidence_provenance": ["APPROVED_REFERENCE"]},
            {"claim_id": "sample-r", "status": "CUSTOMER_CONFIRMATION_PENDING", "evidence_provenance": ["APPROVED_REFERENCE"], "sample_flagged": True},
        ]
    }
    assert firewall.audit_transition(before, after_good) == []


def test_rule_wiring(root: Path):
    router = yaml.safe_load((root / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    coverage = yaml.safe_load((root / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))
    challenge = (root / "references/HOLISTIC_ENGINEERING_CHALLENGE.md").read_text(encoding="utf-8")
    firewall = (root / "references/REFERENCE_EXPOSURE_FIREWALL.md").read_text(encoding="utf-8")
    identity = (root / "references/PART_IDENTITY_GRAPH.md").read_text(encoding="utf-8")

    assert router["release"] == "V4.33"
    assert coverage["release"] == "V4.33"
    for path in [
        "references/HOLISTIC_ENGINEERING_CHALLENGE.md",
        "references/REFERENCE_EXPOSURE_FIREWALL.md",
        "references/PART_IDENTITY_GRAPH.md",
    ]:
        assert path in router["default_load"]
    for check in [
        "holistic_engineering_challenge",
        "views_only_source_view_completeness",
        "final_engineering_sanity_review",
        "source_only_snapshot_before_reference",
        "no_post_reference_source_rewrite",
    ]:
        assert check in router["post_route_checks"]

    for token in [
        "AI_INTERPRETATION_GAP",
        "VIEWS_ONLY_SOURCE_VIEW_COMPLETENESS",
        "FINAL_ENGINEERING_SANITY_REVIEW",
    ]:
        assert token in challenge
    assert "SOURCE_ONLY_SNAPSHOT" in firewall
    assert "CUSTOMER_CONFIRMATION_PENDING" in firewall
    assert "PART_IDENTITY_COLLISION" in identity


def main():
    root = Path(__file__).resolve().parents[2]
    test_holistic_guard(root)
    test_reference_firewall(root)
    test_rule_wiring(root)
    print("PASS: V4.33 521007-07 holistic challenge + reference exposure firewall")


if __name__ == "__main__":
    main()
