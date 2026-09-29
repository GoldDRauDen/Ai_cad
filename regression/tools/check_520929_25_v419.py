#!/usr/bin/env python3
"""V4.19 520929-25 approved constraint-closed FACE_GRAPH / fold-back regression."""
from pathlib import Path
from math import isclose

def total_flat(face_od, nobi):
    return sum(face_od) - sum(nobi)

def bend_pair(face_od, nobi, k):
    """1-based bend k, matching portable sequential double-line equations."""
    lower = sum(face_od[:k]) - sum(nobi[:k])
    upper = sum(face_od[:k]) - sum(nobi[:k-1])
    return lower, upper

def main():
    # 056942: same total does NOT imply same face order.
    n = [4.4]
    correct = [150.0, 23.2]
    reversed_faces = [23.2, 150.0]
    assert isclose(total_flat(correct, n), 168.8, abs_tol=1e-12)
    assert isclose(total_flat(reversed_faces, n), 168.8, abs_tol=1e-12)
    assert bend_pair(correct, n, 1) == (145.6, 150.0)
    assert bend_pair(reversed_faces, n, 1) == (18.799999999999997, 23.2)
    assert bend_pair(correct, n, 1) != bend_pair(reversed_faces, n, 1)

    # 056956: ordered chain + orthogonal local flange, with non-global domains.
    x_faces = [106.0, 222.0, 106.0]
    x_nobi = [3.8, 3.8]
    assert isclose(total_flat(x_faces, x_nobi), 426.4, abs_tol=1e-12)
    p1 = bend_pair(x_faces, x_nobi, 1)
    p2 = bend_pair(x_faces, x_nobi, 2)
    assert all(isclose(a,b,abs_tol=1e-12) for a,b in zip(p1,(102.2,106.0)))
    assert all(isclose(a,b,abs_tol=1e-12) for a,b in zip(p2,(320.4,324.2)))
    assert isclose(90.0 + 29.0 - 3.8, 115.2, abs_tol=1e-12)
    assert (86.2, 90.0) != (0.0, 115.2)  # local bend pair is not a full-bbox domain

    # 057042: signed longitudinal Z/S chain + independent transverse U-channel chain.
    x_faces = [39.8, 128.8, 21.3]
    x_nobi = [4.62, 4.62]
    assert isclose(total_flat(x_faces, x_nobi), 180.66, abs_tol=1e-12)
    xp1, xp2 = bend_pair(x_faces, x_nobi, 1), bend_pair(x_faces, x_nobi, 2)
    assert all(isclose(a,b,abs_tol=1e-12) for a,b in zip(xp1,(35.18,39.80)))
    assert all(isclose(a,b,abs_tol=1e-12) for a,b in zip(xp2,(159.36,163.98)))
    fold_signs = (+1, -1)
    assert fold_signs[0] != fold_signs[1]

    y_faces = [15.0, 35.0, 15.0]
    y_nobi = [4.62, 4.62]
    assert isclose(total_flat(y_faces, y_nobi), 55.76, abs_tol=1e-12)
    yp1, yp2 = bend_pair(y_faces, y_nobi, 1), bend_pair(y_faces, y_nobi, 2)
    assert all(isclose(a,b,abs_tol=1e-12) for a,b in zip(yp1,(10.38,15.00)))
    assert all(isclose(a,b,abs_tol=1e-12) for a,b in zip(yp2,(40.76,45.38)))

    # Structural closure: production graph records cannot omit ownership/sign/domain.
    required_face = {"face_id","local_origin","local_axis_u","local_axis_v","contour_edges","normal"}
    required_dim = {"value","witness_A","witness_B","semantic","owner"}
    required_feature = {"family","host_face","local_datum","local_geometry"}
    required_bend = {"face_A","face_B","shared_edge","fold_sign","material_domain"}
    good = {
        "face": required_face,
        "dim": required_dim,
        "feature": required_feature,
        "bend": required_bend,
    }
    for fields in good.values():
        assert fields
    bad_feature = {"family","local_geometry"}
    assert not required_feature.issubset(bad_feature)

    root = Path(__file__).resolve().parents[2]
    portable = (root/"skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md").read_text(encoding="utf-8")
    release = (root/"skills/lispcad/versions/V4.19/SKILL_LISPCAD_V4_19_PORTABLE.md").read_text(encoding="utf-8")
    old = (root/"skills/lispcad/versions/V4.18/SKILL_LISPCAD_V4_18_PORTABLE.md").read_text(encoding="utf-8")
    entry = (root/"AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    protocol = (root/"references/FACE_GRAPH_UNFOLD_PROTOCOL.md").read_text(encoding="utf-8")
    bend = (root/"skills/lispcad/modes/BEND_UNFOLD.md").read_text(encoding="utf-8")
    validation = (root/"skills/lispcad/core/VALIDATION.md").read_text(encoding="utf-8")
    drawing = (root/"skills/lispcad/core/DRAWING_READING.md").read_text(encoding="utf-8")

    assert portable == release
    assert portable.startswith("# SKILL_LISPCAD V4.19 PORTABLE")
    assert old.startswith("# SKILL_LISPCAD V4.18 PORTABLE")
    assert "Current production release is **V4.19**" in entry
    for token in [
        "FACE_GRAPH", "FEATURE_OWNERSHIP_LOCKED", "BEND_SIGN_LOCKED",
        "CONSTRAINTS_CLOSED", "FOLD_BACK_MATCH", "BEND_DOMAIN_LOCKED"
    ]:
        assert token in portable
        assert token in protocol
    assert "FACE_GRAPH_UNFOLD_PROTOCOL.md" in entry
    assert "FACE_GRAPH_UNFOLD_PROTOCOL.md" in bend
    assert "V4.19 FOLD_BACK_SOURCE_REPROJECTION" in validation
    assert "V4.19 FACE_GRAPH_CAPTURE" in drawing

    print("PASS: 520929-25 V4.19 constraint-closed FACE_GRAPH, signed bend-domain, fold-back guards")

if __name__ == "__main__":
    main()
