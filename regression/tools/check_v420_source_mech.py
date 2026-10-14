#!/usr/bin/env python3
"""V4.20 source/data + mechanical feature regression."""
import math

def data_pdf_flag(delta, customer=None):
    d=abs(float(delta))
    return d >= (1.0 if str(customer)=="433" else 0.1)

def slit_depth_gt90(t, theta):
    if not (90.0 < theta < 180.0):
        raise ValueError("requires 90<theta<180")
    return t*math.sin(math.radians(theta))

def main():
    assert not data_pdf_flag(0.099999)
    assert data_pdf_flag(0.1)
    assert data_pdf_flag(0.100001)
    assert not data_pdf_flag(0.999999,433)
    assert data_pdf_flag(1.0,433)

    exp={150:1.6,130:2.45134221798073,110:3.007016386514907}
    for a,e in exp.items():
        assert abs(slit_depth_gt90(3.2,a)-e)<1e-12
    assert abs((3.2+0.2)-3.4)<1e-12

    rc=23.4; w=6.0
    assert abs(rc+w/2-26.4)<1e-12
    assert abs(rc-w/2-20.4)<1e-12
    assert abs(w/2-3.0)<1e-12
    print("PASS: V4.20 strict DATA/PDF threshold, KH433 exception, >90 slit depth, curved-slot radii")

if __name__=="__main__":
    main()
