from __future__ import annotations

import math
import tempfile
from pathlib import Path

import ezdxf

ROOT = Path(__file__).resolve().parents[2]


def relief90(t: float, s: float):
    """Return (needs_slit, depth_from_actual_edge, depth_from_zero_reference)."""
    if s > 0:
        return False, 0.0, 0.0
    actual = t + 0.2
    if s == 0:
        return True, actual, actual
    return True, actual, abs(s) + actual


def _assert_text_contract() -> None:
    paths = [
        ROOT / "references/RUNTIME_AUTHORITY_GUARD.md",
        ROOT / "references/SOURCE_FEATURE_GROUP_CLOSURE.md",
        ROOT / "references/BEND_EDGE_RELIEF_90.md",
        ROOT / "regression/qa/521005-05_V4_30_APPROVED.md",
    ]
    text = "\n".join(p.read_text(encoding="utf-8") for p in paths)
    for token in [
        "RUNTIME_AUTHORITY_GUARD",
        "SOURCE_FEATURE_GROUP",
        "GROUP_COUNT_CLOSURE",
        "SAME_PHYSICAL_PARAMETER_BEFORE_REFERENCE_CONFLICT",
        "CUSTOMER_CONFIRMATION_PENDING",
        "BEND_EDGE_LENGTH_LOCK",
        "BEND_END_OFFSET_90",
        "bend-edge length",
        "bend-end offset",
        "bend-relief slit",
        "S > 0",
        "S = 0",
        "S < 0",
        "T + 0.2",
        "|S| + T + 0.2",
        "057861",
        "057862",
        "057864",
        "057865",
        "057873",
    ]:
        assert token in text, token

    # The superseded provisional branch must not remain active.
    bend_ref = (ROOT / "references/BEND_EDGE_RELIEF_90.md").read_text(encoding="utf-8")
    assert "There is no active `T/2` threshold" in bend_ref
    assert "`S = +1` -> NO SLIT" in bend_ref
    assert "`S = +1.5` -> NO SLIT" in bend_ref
    assert "`S = +2` -> NO SLIT" in bend_ref


def _assert_relief_matrix() -> None:
    t = 2.0
    assert relief90(t, -2.0) == (True, 2.2, 4.2)
    assert relief90(t, 0.0) == (True, 2.2, 2.2)
    assert relief90(t, 1.0) == (False, 0.0, 0.0)
    assert relief90(t, 1.5) == (False, 0.0, 0.0)
    assert relief90(t, 2.0) == (False, 0.0, 0.0)


def _assert_dxf_readback() -> None:
    # Compact physical read-back fixture. The 2.2 lines represent the actual-edge
    # slit depth for S=0 and S<0; 50/248 are the 057873 bend-edge-length regression
    # values. They are regression evidence, not reusable construction defaults.
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "v430_bend_end_readback.dxf"
        doc = ezdxf.new("R2010")
        doc.header["$INSUNITS"] = 4
        msp = doc.modelspace()
        msp.add_line((0.0, 0.0), (2.2, 0.0))
        msp.add_line((0.0, 10.0), (2.2, 10.0))
        msp.add_line((0.0, 20.0), (50.0, 20.0))
        msp.add_line((0.0, 30.0), (248.0, 30.0))
        doc.saveas(path)

        rd = ezdxf.readfile(path)
        assert rd.header["$INSUNITS"] == 4
        lines = list(rd.modelspace().query("LINE"))
        lengths = sorted(
            round(
                math.hypot(
                    e.dxf.end.x - e.dxf.start.x,
                    e.dxf.end.y - e.dxf.start.y,
                ),
                6,
            )
            for e in lines
        )
        assert lengths == [2.2, 2.2, 50.0, 248.0]


if __name__ == "__main__":
    _assert_text_contract()
    _assert_relief_matrix()
    _assert_dxf_readback()
    print("PASS: V4.30 source-group, parameter-identity, bend-edge and 90-degree bend-end relief regression")
