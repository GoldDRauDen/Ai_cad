"""Small upstream helper for APPROVED V4.10 signed source-datum mapping.

This arithmetic helper does NOT detect an origin from a PDF or prove drawing evidence.
The caller must independently prove the physical source zero, source +axis direction,
and its position in the TARGET CAD coordinate frame (Section 4.2.9).
"""
from math import isfinite
from numbers import Real


def source_ordinate_to_cad(source_value_mm, *, source_origin_cad_mm, source_positive_cad):
    """Map one proven absolute source ordinate to the selected CAD axis.

    source_positive_cad must be +1 if increasing source values point along
    the selected CAD-positive axis, or -1 when opposite. The caller provides
    the SOURCE origin's actual coordinate in the TARGET CAD frame.
    """
    if isinstance(source_positive_cad, bool) or source_positive_cad not in (-1, 1):
        raise ValueError("Source positive axis direction must be proved as +1 or -1")
    for value, name in ((source_value_mm, "source ordinate"),
                        (source_origin_cad_mm, "source origin in CAD")):
        if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(value):
            raise ValueError(f"Proved finite {name} required")
    return source_origin_cad_mm + source_positive_cad * source_value_mm


def source_xy_to_cad(source_xy, *, source_origin_cad_xy, source_positive_cad_xy):
    """Aligned orthographic source→CAD mapping; no implicit origin or axis signs.

    For rotated/axis-swapped source views use an independently proved view
    transformation; do not force this helper onto a rotated view.
    """
    if len(source_xy) != 2 or len(source_origin_cad_xy) != 2 or len(source_positive_cad_xy) != 2:
        raise ValueError("Two independently proved X/Y source values, origins and directions required")
    return (
        source_ordinate_to_cad(source_xy[0], source_origin_cad_mm=source_origin_cad_xy[0],
                               source_positive_cad=source_positive_cad_xy[0]),
        source_ordinate_to_cad(source_xy[1], source_origin_cad_mm=source_origin_cad_xy[1],
                               source_positive_cad=source_positive_cad_xy[1]),
    )
