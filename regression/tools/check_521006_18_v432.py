#!/usr/bin/env python3
"""V4.32 521006-18 bend attachment and formed-profile OD regression."""
from math import isclose
from pathlib import Path

import yaml

def release_number(value):
    return int(str(value).upper().replace("V4.", ""))


FORBIDDEN_ATTACHMENT_EVIDENCE = {
    "NEAREST_VIEW_EDGE",
    "PAPER_PROXIMITY",
    "VIEW_ABOVE_BELOW",
    "VISUAL_SYMMETRY",
}


def flat_length(ods, nobis):
    return sum(ods) - sum(nobis)


def notch_depth_from_center(center_setback, radius):
    return center_setback + radius


def normalize_180(points, width, height):
    return sorted((round(width - x, 6), round(height - y, 6)) for x, y in points)


def test_numeric_regression_facts():
    # 058653: actual outside contributions must be established before Nobi.
    correct_653 = flat_length([25.60, 22.92, 68.00], [1.32, 2.64])
    wrong_653 = flat_length([24.00, 22.00, 68.00], [1.32, 2.64])
    assert isclose(correct_653, 112.56, abs_tol=1e-9)
    assert isclose(wrong_653, 110.04, abs_tol=1e-9)
    assert not isclose(correct_653, wrong_653, abs_tol=1e-9)

    # 058655: formed-profile outside lengths, then Nobi.
    correct_655 = flat_length([60.51, 52.81, 32.30], [0.68, 3.80])
    wrong_655 = flat_length([60.00, 50.00, 30.00], [0.68, 3.80])
    assert isclose(correct_655, 141.14, abs_tol=1e-9)
    assert isclose(wrong_655, 135.52, abs_tol=1e-9)

    # 058649/058650: R3 + center setback 5 = physical overall notch depth 8.
    assert isclose(notch_depth_from_center(5.0, 3.0), 8.0, abs_tol=1e-12)
    assert isclose(notch_depth_from_center(8.0, 3.0), 11.0, abs_tol=1e-12)

    # 058652 control: a 180-degree whole-part representation is equivalent after normalization.
    w, h = 60.0, 107.92
    pts = [(15.0, 56.0), (45.0, 56.0), (18.0, 97.92), (42.0, 97.92)]
    rotated = [(w-x, h-y) for x, y in pts]
    assert normalize_180(rotated, w, h) == sorted((round(x, 6), round(y, 6)) for x, y in pts)


def test_attachment_evidence_contract():
    # 058648 mechanism: nearest graphical edge can never be the proof.
    evidence = {"FORMED_PROFILE_TOPOLOGY", "VIEW_CORRESPONDENCE"}
    assert evidence.isdisjoint(FORBIDDEN_ATTACHMENT_EVIDENCE)
    wrong = {"NEAREST_VIEW_EDGE"}
    assert not wrong.isdisjoint(FORBIDDEN_ATTACHMENT_EVIDENCE)

    record = {
        "face_A_shared_edge": "FACE_MAIN.TOP",
        "face_B_shared_edge": "FACE_FLANGE.PHYSICAL_BEND_EDGE",
        "face_B_free_edge": "FACE_FLANGE.OPPOSITE_FREE_EDGE",
    }
    assert record["face_B_shared_edge"] != record["face_B_free_edge"]


def test_rule_wiring():
    root = Path(__file__).resolve().parents[2]
    edge = (root / "references/BEND_ATTACHMENT_EDGE_OWNERSHIP.md").read_text(encoding="utf-8")
    od = (root / "references/FORMED_PROFILE_OD_MEASUREMENT.md").read_text(encoding="utf-8")
    face = (root / "references/FACE_GRAPH_UNFOLD_PROTOCOL.md").read_text(encoding="utf-8")
    datum = (root / "skills/lispcad/core/DATUM_DIMENSION.md").read_text(encoding="utf-8")
    cross = (root / "skills/lispcad/core/CROSS_FEATURE_VALIDATION.md").read_text(encoding="utf-8")
    router = yaml.safe_load((root / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    coverage = yaml.safe_load((root / "skills/lispcad/router/RULE_COVERAGE.yaml").read_text(encoding="utf-8"))

    text = "\n".join([edge, od, face, datum, cross])
    for token in [
        "BEND_ATTACHMENT_EDGE_LOCKED",
        "NEAREST_VIEW_EDGE",
        "MEASUREMENT_CONSTRUCTION_VIEW",
        "FACE_2.BEND_EDGE",
        "FACE_2.FREE_EDGE",
        "OD_actual",
        "R3",
        "overall depth",
    ]:
        assert token in text

    for mode in ["BEND", "MULTI_FACE", "UNKNOWN"]:
        loads = router["mode_routes"][mode]["load"]
        assert "references/BEND_ATTACHMENT_EDGE_OWNERSHIP.md" in loads
        assert "references/FORMED_PROFILE_OD_MEASUREMENT.md" in loads

    assert "bend_attachment_edge_lock" in router["post_route_checks"]
    assert "formed_profile_od_measurement_when_applicable" in router["post_route_checks"]
    assert release_number(router["release"]) >= 32
    assert release_number(coverage["release"]) >= 32
    assert "V4.32" in coverage["release_coverage"]


def main():
    test_numeric_regression_facts()
    test_attachment_evidence_contract()
    test_rule_wiring()
    print("PASS: V4.32 521006-18 bend attachment edge ownership + formed-profile OD semantics")


if __name__ == "__main__":
    main()
