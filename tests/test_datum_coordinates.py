"""V4.10 approved DATUM/axis arithmetic regression, not PDF-reading certification."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from datum_coordinates import source_ordinate_to_cad, source_xy_to_cad


@pytest.mark.parametrize("x_source", [50, 225, 400])
def test_043793_three_hole_centers_source_top_left_negative_y(x_source):
    """X values are synthetic independent probes; regression claim is the Y row."""
    x_cad, y_cad = source_xy_to_cad(
        (x_source, -30),
        source_origin_cad_xy=(0, 138),
        source_positive_cad_xy=(+1, +1))
    assert x_cad == x_source
    assert y_cad == 108
    assert y_cad != 88  # previous wrong datum/offset interpretation
    assert y_cad != -30  # signed source Y cannot be copied to bottom-left CAD


def test_top_left_source_axis_pointing_down_has_positive_source_ordinate():
    assert source_ordinate_to_cad(
        30, source_origin_cad_mm=138, source_positive_cad=-1) == 108


def test_bottom_left_source_and_cad_frames_coincide_when_proved():
    assert source_xy_to_cad(
        (50, 108), source_origin_cad_xy=(0, 0),
        source_positive_cad_xy=(+1, +1)) == (50, 108)


def test_mirrored_source_x_requires_explicit_negative_sign():
    assert source_xy_to_cad(
        (12, -30), source_origin_cad_xy=(120, 138),
        source_positive_cad_xy=(-1, +1)) == (108, 108)


@pytest.mark.parametrize("direction", [None, 0, 2, "up", True, -2])
def test_unknown_axis_direction_cannot_be_used_for_production(direction):
    with pytest.raises(ValueError, match="direction"):
        source_ordinate_to_cad(-30, source_origin_cad_mm=138,
                               source_positive_cad=direction)


@pytest.mark.parametrize("bad_origin", [None, float("nan"), float("inf"), "138", True])
def test_missing_or_unproved_source_origin_rejected(bad_origin):
    with pytest.raises(ValueError, match="origin"):
        source_ordinate_to_cad(-30, source_origin_cad_mm=bad_origin,
                               source_positive_cad=+1)


def test_xy_transform_requires_both_axes():
    with pytest.raises(ValueError, match="Two"):
        source_xy_to_cad((50,), source_origin_cad_xy=(0, 138),
                         source_positive_cad_xy=(+1, +1))
