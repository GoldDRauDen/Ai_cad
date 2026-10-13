#!/usr/bin/env python3
"""Source-witness slot anchor semantics; never infer anchor from slot appearance."""
from __future__ import annotations

import math

ANCHORS = {"SLOT_MIDPOINT", "ARC_CENTER_1", "ARC_CENTER_2", "OUTER_TIP_1", "OUTER_TIP_2"}


class SlotAnchorError(ValueError):
    pass


def slot_midpoint(anchor, kind, axis, width_mm, center_distance_mm):
    if kind not in ANCHORS:
        raise SlotAnchorError("SLOT_ANCHOR_UNCLASSIFIED")
    try:
        w, c = float(width_mm), float(center_distance_mm)
        ax, ay = float(axis[0]), float(axis[1])
        px, py = float(anchor[0]), float(anchor[1])
    except (TypeError, ValueError, IndexError) as exc:
        raise SlotAnchorError("SLOT_ANCHOR_INVALID") from exc
    if not all(math.isfinite(v) for v in (w, c, ax, ay, px, py)) or w <= 0 or c < 0:
        raise SlotAnchorError("SLOT_SIZE_INVALID")
    length = math.hypot(ax, ay)
    if not math.isclose(length, 1.0, abs_tol=1e-8):
        raise SlotAnchorError("SLOT_AXIS_NOT_UNIT")
    offset = {
        "SLOT_MIDPOINT": 0.0, "ARC_CENTER_1": c / 2, "ARC_CENTER_2": -c / 2,
        "OUTER_TIP_1": (c + w) / 2, "OUTER_TIP_2": -(c + w) / 2,
    }[kind]
    return (px + offset * ax, py + offset * ay)


def validate_slot_anchor(record):
    try:
        if not record.get("source_pdf_page") or not record.get("evidence_ref") or record.get("witness_verified") is not True:
            raise SlotAnchorError("SLOT_WITNESS_UNPROVED")
        expected = slot_midpoint(
            record["anchor_point"], record["anchor_type"], record["axis_unit"],
            record["width_mm"], record["center_distance_mm"],
        )
        total = record["width_mm"] + record["center_distance_mm"]
        if abs(total - float(record["overall_length_mm"])) > 1e-8:
            raise SlotAnchorError("SLOT_LENGTH_SEMANTICS_MISMATCH")
        actual = tuple(float(v) for v in record["canonical_midpoint"])
        if len(actual) != 2 or math.hypot(expected[0]-actual[0], expected[1]-actual[1]) > 1e-7:
            raise SlotAnchorError("SLOT_ANCHOR_MISMATCH")
    except SlotAnchorError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise SlotAnchorError("SLOT_ANCHOR_RECORD_INCOMPLETE") from exc
    return expected
