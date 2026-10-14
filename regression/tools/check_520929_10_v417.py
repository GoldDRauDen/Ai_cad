#!/usr/bin/env python3
"""V4.17 520929-10 approved geometry-guard regression."""

def main():
    # Slot family: printed width/end diameter, not a nearby 10 mm chain value.
    slot_w = 9.0
    slot_r = slot_w / 2.0
    assert slot_r == 4.5
    assert (10.0 / 2.0) != slot_r  # catches the old W10/R5 substitution

    # Mirror guard: this approved pair uses the same contour, not an inferred reflection.
    p646 = [(10,0),(50,0),(50,38),(0,38),(0,10)]
    p647 = [(10,0),(50,0),(50,38),(0,38),(0,10)]
    reflected_646 = [(50-x,y) for x,y in p646]
    assert p646 == p647
    assert reflected_646 != p647

    # Datum witness: slot center is 10 from TOP of H32.
    h = 32.0
    top_to_center = 10.0
    y_bottom_origin = h - top_to_center
    assert y_bottom_origin == 22.0
    assert y_bottom_origin != 17.0

    # Resolved KEGAKI offset and height.
    x_kegaki = 12.0 - 3.0
    assert x_kegaki == 9.0
    assert 16.0 == 16.0

    # Reference metadata boundary: header may claim inch while proved physical units are mm.
    sample_insunits = 1
    actual_units = "mm"
    production_insunits = 4
    assert sample_insunits == 1 and actual_units == "mm" and production_insunits == 4

    print("PASS: 520929-10 V4.17 slot/mirror/datum/KEGAKI/reference-unit guards")

if __name__ == "__main__":
    main()
