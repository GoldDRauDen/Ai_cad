# SILT_GT90 V4.20 — approved >90° bend-slit depth regression

**Direct user approval:** 2026-09-29.

The supplied DXF contains three examples at t=3.2 with included bend angles >90°.

Expected relation: `D=t*sin(theta)`, for `90°<theta<180°`.

Assertions:
- 150° -> 1.600000000 mm
- 130° -> 2.45134221798 mm
- 110° -> 3.00701638651 mm

Equivalent reflex-angle form is `t*abs(sin(phi))`.

FAIL if using constant t/2 for every >90° bend; FAIL if applying this formula at exactly 90° (90° uses t+0.2); FAIL if slit depth is confused with Nobi.
