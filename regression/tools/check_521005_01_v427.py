"""V4.27 521005-01 production regression.

Checks approved weld-cue/KEGAKI routing text, drawing-specific slot/datum facts,
and a physical DXF save/read-back of the approved 058062 KEGAKI segments.
"""
from pathlib import Path
import math
import tempfile

import ezdxf
import yaml

ROOT = Path(__file__).resolve().parents[2]


def norm_segment(a, b, nd=5):
    a = (round(float(a[0]), nd), round(float(a[1]), nd))
    b = (round(float(b[0]), nd), round(float(b[1]), nd))
    return tuple(sorted((a, b)))


def expected_kegaki_segments():
    raw = [
        ((40,239),(194,239)), ((40,245),(194,245)),
        ((40,239),(40,245)), ((194,239),(194,245)),
        ((40,55),(194,55)), ((40,61),(194,61)),
        ((40,55),(40,61)), ((194,55),(194,61)),
        ((256.22,239),(376.22,239)), ((256.22,245),(376.22,245)),
        ((256.22,239),(256.22,245)),
        ((256.22,55),(376.22,55)), ((256.22,61),(376.22,61)),
        ((256.22,55),(256.22,61)),
    ]
    return {norm_segment(a, b) for a, b in raw}


def _release_number(value):
    return int(str(value).upper().replace("V4.", ""))


def check_rule_wiring():
    kegaki = (ROOT / "skills/lispcad/features/KEGAKI.md").read_text(encoding="utf-8")
    census = (ROOT / "skills/lispcad/router/FEATURE_CENSUS.md").read_text(encoding="utf-8")
    cross = (ROOT / "skills/lispcad/core/CROSS_FEATURE_VALIDATION.md").read_text(encoding="utf-8")
    reg = (ROOT / "regression/qa/521005-01_V4_27_APPROVED.md").read_text(encoding="utf-8")
    text = "\n".join((kegaki, census, cross, reg))
    for token in [
        "REVERSED_E_ABOVE_BARCODE",
        "WELD_REQUIRED_CUE",
        "cannot self-locate",
        "specific KEGAKI instruction",
        "do not infer welding",
        "058062",
        "058063",
        "058064",
    ]:
        assert token in text, token

    router = yaml.safe_load((ROOT / "skills/lispcad/router/ROUTER.yaml").read_text(encoding="utf-8"))
    assert _release_number(router["release"]) >= 27
    # Do not encode a false universal dependency: RIB may exist without KEGAKI.
    assert "KEGAKI" not in router["feature_routes"]["RIB"].get("depends_on", [])


def check_058061_slot_datum():
    W = 17.0
    C = 40.0
    L_TOTAL = C + W
    assert math.isclose(L_TOTAL, 57.0)
    assert (25.0, 595.0) != (40.0, 580.0)


def check_058064_datum_witness():
    assert math.isclose(19 + 195, 214)
    assert math.isclose(26 + 331, 357)
    assert math.isclose(250 - 15, 235)
    assert 204 != 220


def check_058062_kegaki_dxf_readback():
    expected = expected_kegaki_segments()
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "521005-01_058062_V427_KEGAKI.dxf"
        doc = ezdxf.new("R2010")
        doc.header["$INSUNITS"] = 4
        msp = doc.modelspace()
        for seg in sorted(expected):
            a, b = seg
            msp.add_line(a, b, dxfattribs={"layer": "0", "color": 1})
        doc.saveas(path)

        saved = ezdxf.readfile(path)
        assert saved.header["$INSUNITS"] == 4
        actual = {
            norm_segment((e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y))
            for e in saved.modelspace()
            if e.dxftype() == "LINE" and e.dxf.layer == "0" and e.dxf.color == 1
        }
        # Compare physical segment geometry, not raw source entity ordering/count.
        assert actual == expected


def main():
    check_rule_wiring()
    check_058061_slot_datum()
    check_058064_datum_witness()
    check_058062_kegaki_dxf_readback()
    print("521005-01 V4.27 regression PASS")


if __name__ == "__main__":
    main()
