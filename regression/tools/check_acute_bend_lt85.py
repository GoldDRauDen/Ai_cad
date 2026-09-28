#!/usr/bin/env python3
"""Reproduce the approved TrainAiCad <85° acute-bend OD result from source geometry."""
from pathlib import Path
import math
import ezdxf
RIN=0.6
def v(a,b): return (b[0]-a[0],b[1]-a[1])
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def mul(a,s): return (a[0]*s,a[1]*s)
def dot(a,b): return a[0]*b[0]+a[1]*b[1]
def norm(a): return math.hypot(a[0],a[1])
def unit(a):
    n=norm(a); return (a[0]/n,a[1]/n)
def midpoint(a,b): return ((a[0]+b[0])/2,(a[1]+b[1])/2)
def dist(a,b): return norm(sub(a,b))
def line_intersection(p,d,q,e):
    det=d[0]*(-e[1])-(-e[0])*d[1]
    if abs(det)<1e-12: raise RuntimeError("parallel offset lines")
    bb=sub(q,p); s=(bb[0]*(-e[1])-(-e[0])*bb[1])/det
    return add(p,mul(d,s))
def order_points(points):
    out=[]
    for p in points:
        if not any(dist(p,q)<1e-8 for q in out): out.append(p)
    c=(sum(p[0] for p in out)/len(out),sum(p[1] for p in out)/len(out))
    return sorted(out,key=lambda p:math.atan2(p[1]-c[1],p[0]-c[0]))
def edges(points): return [(points[i],points[(i+1)%len(points)]) for i in range(len(points))]
def dims(points):
    ee=edges(points); ll=[dist(a,b) for a,b in ee]; o=sorted(range(4),key=lambda i:ll[i])
    return (ll[o[0]]+ll[o[1]])/2,(ll[o[2]]+ll[o[3]])/2,[ee[o[2]],ee[o[3]]]
def centroid(points): return (sum(p[0] for p in points)/len(points),sum(p[1] for p in points)/len(points))
def orient(edge,other):
    a,b=edge
    if dist(a,other)<=dist(b,other): bend,free=a,b
    else: bend,free=b,a
    return free,bend,unit(v(free,bend))
def normal_toward(a,b,target):
    d=unit(v(a,b)); n=(-d[1],d[0])
    return n if dot(n,sub(target,midpoint(a,b)))>=0 else (-n[0],-n[1])
def angle(d1,d2):
    c=max(-1,min(1,abs(dot(unit(d1),unit(d2)))))
    return math.degrees(math.acos(c))
def ldist(p,a,d):
    n=(-d[1],d[0]); return abs(dot(sub(p,a),n))
def points(lines):
    return order_points([(e.dxf.start.x,e.dxf.start.y) for e in lines]+[(e.dxf.end.x,e.dxf.end.y) for e in lines])
def solve(fixture):
    m=ezdxf.readfile(fixture).modelspace()
    a=list(m.query('LINE[layer=="FACE_1"]')); b=list(m.query('LINE[layer=="FACE_2"]'))
    if len(a)!=4 or len(b)!=4: raise RuntimeError("expected 4 LINEs per face")
    p1,p2=points(a),points(b); c1,c2=centroid(p1),centroid(p2)
    t1,L1,e1=dims(p1); t2,L2,e2=dims(p2)
    if abs(t1-t2)>1e-6: raise RuntimeError("thickness mismatch")
    inner1=min(e1,key=lambda e:dist(midpoint(*e),c2)); inner2=min(e2,key=lambda e:dist(midpoint(*e),c1))
    f1,b1,d1=orient(inner1,c2); f2,b2,d2=orient(inner2,c1); alpha=angle(d1,d2)
    if alpha>=85: raise RuntimeError("fixture no longer triggers <85")
    n1,n2=normal_toward(f1,b1,c2),normal_toward(f2,b2,c1)
    C=line_intersection(add(f1,mul(n1,RIN)),d1,add(f2,mul(n2,RIN)),d2)
    assert abs(ldist(C,f1,d1)-RIN)<1e-8 and abs(ldist(C,f2,d2)-RIN)<1e-8
    t=(t1+t2)/2; rout=RIN+t
    return {"t":t,"face_lengths":sorted([L1,L2],reverse=True),"included_angle_deg":alpha,"Rin":RIN,"Rout":rout,
            "center":C,"OD1":dot(C,d1)+rout-dot(f1,d1),"OD2":dot(C,d2)+rout-dot(f2,d2)}
if __name__=="__main__":
    fixture=Path(__file__).resolve().parent.parent/"assets"/"acute_bend_lt85"/"ACUTE_BEND_LT85_SOURCE_FIXTURE.dxf"
    r=solve(fixture)
    print("Derived from normalized source fixture:")
    for k,val in r.items(): print(f"  {k}: {val}")
    EXPECTED_OD1=182.01421719900188; EXPECTED_OD2=49.71223623506498; TOL=0.01
    assert abs(r["OD1"]-EXPECTED_OD1)<TOL and abs(r["OD2"]-EXPECTED_OD2)<TOL
    assert abs(r["t"]-3)<1e-8 and abs(r["included_angle_deg"]-75)<1e-8
    print("PASS: source geometry -> Rin offsets -> center/radii -> outside envelope -> OD1/OD2")
