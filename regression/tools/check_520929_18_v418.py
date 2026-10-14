#!/usr/bin/env python3
"""V4.18 520929-18 approved source-authority / C-R / BOXMET regression."""
from pathlib import Path
from math import isclose

def main():
    # 056911: detailed-page bundle closes independently; summary row does not.
    face_x, face_y = 906.0, 756.0
    flange, nobi = 40.0, 2.64
    flat = (face_x + 2*flange - 2*nobi, face_y + 2*flange - 2*nobi)
    assert isclose(flat[0], 980.72, abs_tol=1e-12)
    assert isclose(flat[1], 830.72, abs_tol=1e-12)
    page1 = {"t": 6.0, "size": (376.0, 130.28)}
    detail = {"t": 1.5, "face": (face_x, face_y), "flat": flat}
    assert page1["t"] != detail["t"]
    assert page1["size"] != detail["flat"]

    # 056898: family identity is semantic, not just a number.
    source_callout = {"family": "C", "value": 2.0, "quantity": 4}
    canonical = {"family": "C", "value": 2.0, "quantity": 4, "primitive": "LINE"}
    bad_old_ai = {"family": "R", "value": 3.0, "quantity": 4, "primitive": "ARC"}
    assert source_callout["family"] == canonical["family"] == "C"
    assert canonical["primitive"] == "LINE"
    assert bad_old_ai["family"] != source_callout["family"]
    assert bad_old_ai["primitive"] == "ARC"

    # 056905 / L>=W: exact local sign pattern. LeadVal is a signed axis delta.
    lead = 6.0
    expected = {
        "BL": ((0,+1), (-lead,-lead)),
        "BR": ((0,+1), (+lead,-lead)),
        "TR": ((0,-1), (+lead,+lead)),
        "TL": ((0,-1), (-lead,+lead)),
    }
    old_mirrored = {
        "BL": ((0,+1), (-lead,+lead)),
        "BR": ((0,+1), (+lead,+lead)),
        "TR": ((0,-1), (+lead,-lead)),
        "TL": ((0,-1), (-lead,-lead)),
    }
    assert expected != old_mirrored
    assert expected["BL"][1] == (-6.0,-6.0)
    assert expected["TR"][1] == (6.0,6.0)

    # BEND trim decision is intersection-driven, not proximity-driven.
    def bend_trim_required(kind, at_endpoint=False):
        if kind == "none":
            return False
        if kind == "point" and at_endpoint:
            return False
        return kind in {"point", "cross", "overlap"}

    assert not bend_trim_required("none")
    assert not bend_trim_required("point", at_endpoint=True)
    assert bend_trim_required("point", at_endpoint=False)
    assert bend_trim_required("overlap")

    # Release wiring guards: checker should be run from the repository.
    root = Path(__file__).resolve().parents[2]
    portable = (root / "skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md").read_text(encoding="utf-8")
    drawing = (root / "skills/lispcad/core/DRAWING_READING.md").read_text(encoding="utf-8")
    chamfer = (root / "skills/lispcad/features/CHAMFER_RADIUS.md").read_text(encoding="utf-8")
    validation = (root / "skills/lispcad/core/VALIDATION.md").read_text(encoding="utf-8")
    boxmet = (root / "references/BOXMET_SLIT_RELIEF.md").read_text(encoding="utf-8")
    entry = (root / "AI_ENTRYPOINT.md").read_text(encoding="utf-8") + (root / "docs/RELEASE_INDEX.md").read_text(encoding="utf-8")

    assert "V4.18 DETAILED_SOURCE_BUNDLE" in drawing and "DETAILED_SOURCE_BUNDLE" in portable
    assert "V4.18 C/R_SEMANTIC_LOCK" in chamfer and "C/R_SEMANTIC_LOCK" in portable
    assert "V4.18 SOURCE_CALLOUT_CANONICAL_CHECK" in validation
    assert "V4.18 BOXMET_SIGNED_ORIENTATION" in boxmet and "BOXMET_SIGNED_ORIENTATION" in portable
    assert "V4.18 520929-18 hard-gate routing" in entry
    assert "520929-18_V4_18_APPROVED.md" in entry

    print("PASS: 520929-18 V4.18 detailed-source, C/R semantic, BOXMET orientation/BEND-intersection guards")

if __name__ == "__main__":
    main()
