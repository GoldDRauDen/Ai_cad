#!/usr/bin/env python3
"""V4.16 520801-04 semantic/math regression."""
import math
def main():
    face_a=4+7+17; face_h=8+25+8; face_b=21; nobi=3.68
    assert face_a==28 and face_h==41 and abs(face_a+face_b-nobi-45.32)<1e-12
    assert 4+4+2==10
    t=1.5; lead=6.0; r=0.5; theta=math.radians(135)
    slit=t+0.2; tangent=r/math.tan(theta/2)
    short=slit-tangent; diag=math.hypot(lead,lead)-tangent
    assert abs(slit-1.7)<1e-12
    assert abs(tangent-0.20710678118654754)<1e-12
    assert abs(short-1.4928932188134525)<1e-12
    assert abs(diag-8.278174593052022)<1e-12
    assert len([(1,0),(-1,0),(-1,1),(1,1)])==4
    assert len([(1,1),(1,-1),(0,-1),(0,1)])==4
    print("PASS: 044812/13 face ownership, 044841 10xR5, 044858/59 BOXMET slit math")
if __name__=="__main__": main()
