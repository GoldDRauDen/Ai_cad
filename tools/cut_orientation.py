#!/usr/bin/env python3
"""Single-cut DXF pose only; do not mutate canonical/composite geometry."""
from __future__ import annotations

import math
from ezdxf import bbox
from ezdxf.math import Matrix44

class OrientationError(ValueError):
    pass


def rotation_for_part(part, width, height):
    grain = part.get("grain", {})
    has_hl = grain.get("is_hl", False)
    if has_hl:
        vector = grain.get("direction_xy")
        proof = grain.get("evidence_ref")
        if not isinstance(vector, (list, tuple)) or len(vector) != 2 or not proof:
            raise OrientationError("HL_DIRECTION_UNPROVED")
        try:
            x, y = (float(i) for i in vector)
        except (ValueError, TypeError) as exc:
            raise OrientationError("HL_DIRECTION_INVALID") from exc
        if not all(math.isfinite(v) for v in (x, y)) or math.hypot(x, y) <= 1e-10:
            raise OrientationError("HL_DIRECTION_INVALID")
        return -math.atan2(y, x)
    return math.pi / 2 if height > width + 1e-7 else 0.0


def orient_cut_doc(doc, part):
    msp = doc.modelspace()
    bounds = bbox.extents(msp, fast=False)
    if not bounds.has_data:
        raise OrientationError("NO_CUT_GEOMETRY")
    w, h = bounds.extmax.x - bounds.extmin.x, bounds.extmax.y - bounds.extmin.y
    angle = rotation_for_part(part, w, h)
    if abs(angle) > 1e-12:
        matrix = Matrix44.z_rotate(angle)
        for ent in msp:
            ent.transform(matrix)
    bounds = bbox.extents(msp, fast=False)
    dx, dy = -bounds.extmin.x, -bounds.extmin.y
    transform = Matrix44.translate(dx, dy, 0)
    for ent in msp:
        ent.transform(transform)
    final = bbox.extents(msp, fast=False)
    if not part.get("grain", {}).get("is_hl") and (
        final.extmax.x-final.extmin.x + 1e-6 < final.extmax.y-final.extmin.y
    ):
        raise OrientationError("PART_ORIENTATION_MISMATCH")
    return {"rotation_deg": round(math.degrees(angle), 12),
            "translation_mm": [round(dx, 10), round(dy, 10)],
            "grain_along_x": bool(part.get("grain", {}).get("is_hl")),
            "final_bbox_mm": [round(final.extmax.x-final.extmin.x, 9),
                              round(final.extmax.y-final.extmin.y, 9)]}
